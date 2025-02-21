# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import contextlib
import logging
import os

import fastapi
import fastapi_pagination
import starlette_prometheus
import uvicorn
from fastapi import middleware, responses, routing
from fastapi.middleware import cors
from fastapi.openapi import utils as fastapi_openapi_utils

import capellacollab.projects.toolmodels.backups.runs.interface as pipeline_runs_interface
from capellacollab import openapi as capellacollab_openapi

# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.configuration.app import config
from capellacollab.core import logging as core_logging
from capellacollab.core.database import engine, migration
from capellacollab.routes import router
from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions import idletimeout, operators

from . import __version__, metrics, redirects

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

ALLOW_ORIGINS = [
    f"{config.general.scheme}://{config.general.host}:{config.general.port}"
]


@contextlib.asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    del _app

    migration.migrate_db(engine, config.database.url)

    # Load the Kubernetes configuration at startup
    operators.get_operator()

    idletimeout.terminate_idle_sessions_in_background()
    pipeline_runs_interface.schedule_refresh_and_trigger_pipeline_jobs()
    sessions_auth.initialize_session_pre_authentication()

    metrics.register_metrics()

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("kubernetes.client.rest").setLevel("INFO")

    logging.info("Startup completed.")

    yield

    logging.getLogger("uvicorn.access").disabled = False
    logging.info("Shutdown completed.")


app = fastapi.FastAPI(
    title="Capella Collaboration",
    version=__version__,
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
    lifespan=lifespan,
    openapi_url="/api/docs/openapi.json",
    docs_url="/api/docs/swagger",
    redoc_url="/api/docs/redoc",
)


if config.logging.profiling:
    import pyinstrument

    @app.middleware("http")
    async def profile_request(request: fastapi.Request, call_next):
        profiling = request.query_params.get("profile", False)
        if profiling:
            profiler = pyinstrument.Profiler(async_mode="enabled")
            profiler.start()
            await call_next(request)
            profiler.stop()
            return responses.HTMLResponse(profiler.output_html())
        return await call_next(request)


@app.get(
    "/docs", response_class=responses.RedirectResponse, include_in_schema=False
)
def redirect_docs():
    """Redirect `/docs` to new SwaggerUI documentation location."""
    return responses.RedirectResponse("/api/docs/swagger")


fastapi_pagination.add_pagination(app)


@app.exception_handler(500)
async def handle_exceptions(request: fastapi.Request, exc: Exception):  # noqa: ARG001
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
def healthcheck():
    return {"status": "alive"}


app.add_route("/metrics", starlette_prometheus.metrics)
app.include_router(router, prefix="/api/v1")
app.include_router(redirects.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = fastapi_openapi_utils.get_openapi(
        title="Capella Collaboration Manager API",
        version=__version__,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "PersonalAccessToken": {"type": "http", "scheme": "basic"},
        "Cookie": {
            "type": "apiKey",
            "in": "cookie",
            "name": "id_token",
        },
    }

    openapi_schema["components"]["schemas"] |= (
        capellacollab_openapi.get_exception_schemas()
    )

    openapi_schema["security"] = [
        {"PersonalAccessToken": []},
        {"Cookie": []},
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def use_route_names_as_operation_ids() -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    """
    for route in app.routes:
        if isinstance(route, routing.APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids()
capellacollab_openapi.add_permissions_and_exceptions_to_api_docs(app)
app.openapi = custom_openapi  # type: ignore[method-assign]


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
