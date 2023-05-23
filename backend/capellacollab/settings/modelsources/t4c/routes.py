# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.routes import get_version_by_id_or_raise
from capellacollab.sessions.schema import GetSessionUsageResponse
from capellacollab.settings.modelsources.t4c import crud
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.interface import get_t4c_status
from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CInstance,
    DatabaseT4CInstance,
    PatchT4CInstance,
    T4CInstance,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    router as repositories_router,
)
from capellacollab.users.models import Role

router = APIRouter(
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)


@router.get("", response_model=list[T4CInstance])
def list_t4c_settings(
    db: Session = Depends(get_db),
) -> Sequence[DatabaseT4CInstance]:
    return crud.get_t4c_instances(db)


@router.get(
    "/{t4c_instance_id}",
    response_model=T4CInstance,
)
def get_t4c_instance(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
) -> DatabaseT4CInstance:
    return instance


@router.post(
    "",
    response_model=T4CInstance,
)
def create_t4c_instance(
    body: CreateT4CInstance,
    db: Session = Depends(get_db),
) -> DatabaseT4CInstance:
    version = get_version_by_id_or_raise(db, body.version_id)
    instance = DatabaseT4CInstance(**body.dict())
    instance.version = version
    return crud.create_t4c_instance(db, instance)


@router.patch(
    "/{t4c_instance_id}",
    response_model=T4CInstance,
)
def edit_t4c_instance(
    body: PatchT4CInstance,
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    db: Session = Depends(get_db),
) -> DatabaseT4CInstance:
    return crud.update_t4c_instance(db, instance, body)


@router.get(
    "/{t4c_instance_id}/licenses",
    response_model=GetSessionUsageResponse,
    dependencies=[
        Depends(auth_injectables.RoleVerification(required_role=Role.ADMIN))
    ],
)
def fetch_t4c_licenses(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
) -> GetSessionUsageResponse:
    return get_t4c_status(instance)


router.include_router(
    repositories_router, prefix="/{t4c_instance_id}/repositories"
)
