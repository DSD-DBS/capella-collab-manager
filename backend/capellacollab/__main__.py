# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os

import fastapi
import fastapi_pagination
import starlette_prometheus
import uvicorn
from fastapi import exception_handlers, middleware, responses
from fastapi.middleware import cors

import capellacollab.projects.toolmodels.backups.runs.interface as pipeline_runs_interface
import capellacollab.sessions.metrics as sessions_metrics
import capellacollab.settings.modelsources.t4c.metrics as t4c_metrics

# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core import logging as core_logging
from capellacollab.core.database import engine, migration
from capellacollab.routes import router
from capellacollab.sessions import idletimeout, operators

from . import __version__

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(core_logging.CustomFormatter())

timed_rotating_file_handler = core_logging.CustomTimedRotatingFileHandler(
    str(config.logging.log_path) + "backend.log"
)
timed_rotating_file_handler.setFormatter(
    core_logging.CustomFormatter(colored_output=False)
)

logging.basicConfig(
    level=config.logging.level,
    handlers=[stream_handler, timed_rotating_file_handler],
)


async def startup():
    migration.migrate_db(engine, config.database.url)
    logging.info("Migrations done - Server is running")

    # This is needed to load the Kubernetes configuration at startup
    operators.get_operator()

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("requests_oauthlib.oauth2_session").setLevel("INFO")
    logging.getLogger("kubernetes.client.rest").setLevel("INFO")


async def shutdown():
    logging.getLogger("uvicorn.access").disabled = False
    logging.getLogger("uvicorn.error").disabled = False


app = fastapi.FastAPI(
    title="Capella Collaboration",
    version=__version__,
    on_startup=[
        startup,
        idletimeout.terminate_idle_sessions_in_background,
        sessions_metrics.register,
        t4c_metrics.register,
        pipeline_runs_interface.schedule_refresh_and_trigger_pipeline_jobs,
    ],
    middleware=[
        middleware.Middleware(
            cors.CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
            allow_headers=["*"],
        ),
        middleware.Middleware(core_logging.AttachTraceIdMiddleware),
        middleware.Middleware(core_logging.AttachUserNameMiddleware),
        middleware.Middleware(core_logging.LogExceptionMiddleware),
        middleware.Middleware(core_logging.LogRequestsMiddleware),
        middleware.Middleware(starlette_prometheus.PrometheusMiddleware),
    ],
    on_shutdown=[shutdown],
    openapi_url="/api/docs/openapi.json",
    docs_url="/api/docs/swagger",
    redoc_url="/api/docs/redoc",
)


@app.get(
    "/docs", response_class=responses.RedirectResponse, include_in_schema=False
)
def redirect_docs():
    """Redirect `/docs` to new SwaggerUI documentation location."""
    return responses.RedirectResponse("/api/docs/swagger")


fastapi_pagination.add_pagination(app)


@app.exception_handler(500)
async def handle_exceptions(request: fastapi.Request, exc: Exception):
    # pylint: disable=unused-argument
    """
    A custom exception handler is required, otherwise no CORS headers are included
    in the case of exceptions.
    https://github.com/encode/starlette/issues/1175
    """
    cors_middleware = cors.CORSMiddleware(
        app=app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
        allow_headers=["*"],
    )

    response = responses.JSONResponse(
        status_code=500, content={"body": "Internal Server Error"}
    )
    response.headers.update(cors_middleware.simple_headers)

    return response


@app.get("/healthcheck", tags=["Healthcheck"], include_in_schema=False)
async def healthcheck():
    return {"status": "alive"}


app.add_route("/metrics", starlette_prometheus.metrics)
app.include_router(router, prefix="/api/v1")


async def exception_handler(
    request: fastapi.Request, exc: core_exceptions.BaseError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=exc.status_code,
            detail={
                "title": exc.title,
                "reason": exc.reason,
                "err_code": exc.err_code,
            },
        ),
    )


def register_exceptions():
    for exc in core_exceptions.BaseError.__subclasses__():
        app.add_exception_handler(exc, exception_handler)  # type: ignore[arg-type]


register_exceptions()

if __name__ == "__main__":
    if os.getenv("FASTAPI_AUTO_RELOAD", "").lower() in ("1", "true", "t"):
        logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
        uvicorn.run(
            "capellacollab.__main__:app",
            reload=True,
            reload_dirs=["capellacollab"],
            reload_includes=["*.py", "*.yaml", "*.yml"],
        )
    else:
        uvicorn.run(app)
