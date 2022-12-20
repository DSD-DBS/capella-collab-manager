# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.users.models import Role

from .integrations.purevariants import routes as purevariants
from .modelsources import routes as modelsources

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.USER))]
)
router.include_router(
    modelsources.router,
    prefix="/modelsources",
)
router.include_router(
    purevariants.router, prefix="/integrations/pure-variants"
)
