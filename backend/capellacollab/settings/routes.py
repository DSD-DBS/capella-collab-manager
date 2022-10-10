# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from .modelsources import routes as modelsources

router = APIRouter()
router.include_router(
    modelsources.router,
    prefix="/modelsources",
)
