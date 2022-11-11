# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core.database import engine, migration
from capellacollab.core.logging import (
    AttachTraceIdMiddleware,
    AttachUserNameMiddleware,
    HealthcheckFilter,
    LogRequestsMiddleware,
    MakeTimedRotatingFileHandler,
)
from capellacollab.routes import router, status

logging.basicConfig(
    level=config["logging"]["level"],
    handlers=[
        MakeTimedRotatingFileHandler(
            str(config["logging"]["logPath"]) + "backend.log"
        )
    ],
    format="time=%(asctime)s level=%(levelname)s function=%(funcName)s %(message)s",
)

logging.getLogger("uvicorn.access").addFilter(HealthcheckFilter())


async def startup():
    migration.migrate_db(engine)
    logging.getLogger("uvicorn.access").disabled = True


async def shutdown():
    logging.getLogger("uvicorn.access").disabled = False


app = FastAPI(
    title="Capella Collaboration",
    on_startup=[startup],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
            allow_headers=["*"],
        ),
        Middleware(AttachTraceIdMiddleware),
        Middleware(AttachUserNameMiddleware),
        Middleware(LogRequestsMiddleware),
    ],
    on_shutdown=[shutdown],
)


@app.exception_handler(500)
async def handle_exceptions(request, exc):
    """
    A custom exception handler is required, otherwise no CORS headers are included
    in the case of exceptions.
    https://github.com/encode/starlette/issues/1175
    """
    cors = CORSMiddleware(
        app=app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
        allow_headers=["*"],
    )

    response = JSONResponse(
        status_code=500, content={"body": "Internal Server Error"}
    )
    response.headers.update(cors.simple_headers)

    return response


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.include_router(status.router, prefix="", tags=["Status"])
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app)
