import logging
import random
import string
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# This import statement is required and should not be removed! (Alembic will not work otherwise)
import t4cclient.sql_models
from t4cclient.core.database import __main__ as database
from t4cclient.routes import router, status

logging.basicConfig(level=logging.INFO)

database.migrate_db()


log = logging.getLogger(__name__)


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


logging.getLogger("uvicorn.access").addFilter(HealthcheckFilter())


app = FastAPI(title="T4C Client Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["*"],
)


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.include_router(status.router, prefix="", tags=["Status"])
app.include_router(router, prefix="/api/v1")
