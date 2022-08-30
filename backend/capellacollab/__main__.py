# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import logging
import random
import string
import time
import typing as t

# 3rd party:
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# 1st party:
# This import statement is required and should not be removed! (Alembic will not work otherwise)
from capellacollab.config import config
from capellacollab.core.database import __main__ as database
from capellacollab.routes import router, status

database.migrate_db()


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


logging.getLogger("uvicorn.access").addFilter(HealthcheckFilter())
log.addFilter(HealthcheckFilter())
logging.getLogger(__name__).setLevel(config["logging"]["level"])

app = FastAPI(title="Capella Collaboration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: t.Callable[[Request], t.Awaitable[Response]]
) -> Response:
    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    log.debug(
        "rid=%(idem)s start request path=%(path)s",
        {"idem": idem, "path": request.url.path},
    )
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = str(round(process_time, 2))
    log.debug(
        "rid=%(idem)s completed_in=%(time)sms status_code=%(code)s",
        {"idem": idem, "time": formatted_process_time, "code": response.status_code},
    )

    return response


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.include_router(status.router, prefix="", tags=["Status"])
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app)
