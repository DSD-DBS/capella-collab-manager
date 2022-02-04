import logging

# This import statement is required and should not be removed! (Alembic will not work otherwise)
import t4cclient.sql_models

import logging
import time
import random
import string

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from t4cclient.core.database import __main__ as database
from t4cclient.routes import router

logging.basicConfig(level=logging.INFO)

database.migrate_db()


log = logging.getLogger(__name__)

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
    idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    log.info(f"rid={idem} start request path={request.url.path}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    log.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
    return response


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "alive"}


app.include_router(router, prefix="/api/v1")
