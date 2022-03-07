import logging
import random
import string
import time
from importlib import metadata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# This import statement is required and should not be removed! (Alembic will not work otherwise)
import t4cclient.sql_models
from t4cclient import config
from t4cclient.core.database import __main__ as database
from t4cclient.routes import router, status

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load extension models
eps = (
    metadata.entry_points()["capellacollab.extensions.backups"]
    + metadata.entry_points()["capellacollab.extensions.modelsources"]
)
for ep in eps:
    log.info("Import models of extension %s", ep.name)
    ep.load().models

database.migrate_db()


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


logging.getLogger("uvicorn.access").addFilter(HealthcheckFilter())
logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI(title="T4C Client Manager")

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


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.include_router(status.router, prefix="", tags=["Status"])
app.include_router(router, prefix="/api/v1")
