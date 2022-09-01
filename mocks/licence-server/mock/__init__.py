# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
from sys import prefix

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import routes

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="licence-server-mock")

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


app.include_router(routes.router, prefix="/mock")
