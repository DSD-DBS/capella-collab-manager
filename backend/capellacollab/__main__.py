# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os

import fastapi
import fastapi_pagination
import starlette_prometheus
import uvicorn
from fastapi import middleware, responses, routing
from fastapi.middleware import cors

import capellacollab.projects.toolmodels.backups.runs.interface as pipeline_runs_interface
import capellacollab.sessions.metrics as sessions_metrics
import capellacollab.settings.modelsources.t4c.license_server.metrics as t4c_metrics
from capellacollab import core

# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core import logging as core_logging
from capellacollab.core.database import engine, migration
from capellacollab.feedback import metrics as feedback_metrics
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

ALLOW_ORIGINS = (
    [f"{config.general.scheme}//{config.general.host}:{config.general.port}"]
    + ["http://localhost:4200", "http://127.0.0.1:4200"]
    if core.DEVELOPMENT_MODE
    else []
)


async def startup():
    migration.migrate_db(engine, config.database.url)
    logging.info("Migrations done - Server is running")

    # This is needed to load the Kubernetes configuration at startup
    operators.get_operator()

    logging.getLogger("uvicorn.access").disabled = True
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
        feedback_metrics.register,
        pipeline_runs_interface.schedule_refresh_and_trigger_pipeline_jobs,
    ],
    middleware=[
        middleware.Middleware(
            cors.CORSMiddleware,
            allow_origins=ALLOW_ORIGINS,
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
    origin = request.headers.get("origin")
    response = responses.JSONResponse(
        status_code=500, content={"body": "Internal Server Error"}
    )

    cors_middleware = cors.CORSMiddleware(
        app=app,
        allow_origins=ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
        allow_headers=["*"],
    )
    response.headers.update(cors_middleware.simple_headers)

    if origin and cors_middleware.is_allowed_origin(origin=origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers.add_vary_header("Origin")

    return response


@app.get("/healthcheck", tags=["Healthcheck"], include_in_schema=False)
async def healthcheck():
    return {"status": "alive"}


app.add_route("/metrics", starlette_prometheus.metrics)
app.include_router(router, prefix="/api/v1")


def use_route_names_as_operation_ids() -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    """
    for route in app.routes:
        if isinstance(route, routing.APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids()

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
