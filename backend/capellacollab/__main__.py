# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os

import fastapi
import fastapi_pagination
import starlette_prometheus
import uvicorn
from fastapi import middleware, responses
from fastapi.middleware import cors

import capellacollab.projects.toolmodels.backups.runs.interface as pipeline_runs_interface
import capellacollab.sessions.metrics

# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core import logging as core_logging
from capellacollab.core.database import engine, migration
from capellacollab.core.logging import exceptions as logging_exceptions
from capellacollab.projects.toolmodels import (
    exceptions as toolmodels_exceptions,
)
from capellacollab.projects.toolmodels.backups import (
    exceptions as backups_exceptions,
)
from capellacollab.projects.toolmodels.modelsources.git import (
    exceptions as git_exceptions,
)
from capellacollab.projects.toolmodels.modelsources.git.gitlab import (
    exceptions as gitlab_exceptions,
)
from capellacollab.projects.toolmodels.modelsources.git.handler import (
    exceptions as git_handler_exceptions,
)
from capellacollab.routes import router
from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import idletimeout, operators
from capellacollab.settings.modelsources.t4c import (
    exceptions as settings_t4c_exceptions,
)
from capellacollab.tools import exceptions as tools_exceptions
from capellacollab.users import exceptions as users_exceptions

handlers: list[logging.Handler] = [
    logging.StreamHandler(),
    core_logging.CustomTimedRotatingFileHandler(
        str(config["logging"]["logPath"]) + "backend.log"
    ),
]

for handler in handlers:
    handler.setFormatter(core_logging.CustomFormatter())

logging.basicConfig(level=config["logging"]["level"], handlers=handlers)


async def startup():
    migration.migrate_db(engine, config["database"]["url"])
    logging.info("Migrations done - Server is running")

    # This is needed to load the Kubernetes configuration at startup
    operators.get_operator()

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").disabled = True
    logging.getLogger("requests_oauthlib.oauth2_session").setLevel("INFO")
    logging.getLogger("kubernetes.client.rest").setLevel("INFO")


async def shutdown():
    logging.getLogger("uvicorn.access").disabled = False
    logging.getLogger("uvicorn.error").disabled = False


app = fastapi.FastAPI(
    title="Capella Collaboration",
    on_startup=[
        startup,
        idletimeout.terminate_idle_sessions_in_background,
        capellacollab.sessions.metrics.register,
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
)

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


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.add_route("/metrics", starlette_prometheus.metrics)
app.include_router(router, prefix="/api/v1")


def register_exceptions():
    tools_exceptions.register_exceptions(app)
    toolmodels_exceptions.register_exceptions(app)
    git_exceptions.register_exceptions(app)
    gitlab_exceptions.register_exceptions(app)
    git_handler_exceptions.register_exceptions(app)
    backups_exceptions.register_exceptions(app)
    logging_exceptions.register_exceptions(app)
    core_exceptions.register_exceptions(app)
    users_exceptions.register_exceptions(app)
    sessions_exceptions.register_exceptions(app)
    settings_t4c_exceptions.register_exceptions(app)


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
