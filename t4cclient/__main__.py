from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from t4cclient.core.database import __main__ as database
from t4cclient.routes import router

database.migrate_db()

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


app.include_router(router, prefix="/api/v1")
