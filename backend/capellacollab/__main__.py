# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import random
import string
import time

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from capellacollab.config import config

logging.basicConfig(level=config["logging"]["level"])
log = logging.getLogger(__name__)


# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core.database import engine, migration
from capellacollab.routes import router, status


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


logging.getLogger("uvicorn.access").addFilter(HealthcheckFilter())
log.addFilter(HealthcheckFilter())

app = FastAPI(title="Capella Collaboration")


@app.on_event("startup")
async def startup_event():
    migration.migrate_db(engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    log.debug(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    log.debug(
        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
    )

    return response


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
