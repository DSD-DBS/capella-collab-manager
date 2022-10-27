# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import (
    RoleVerification,
    verify_admin,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.routes import (
    get_version_by_id_or_raise,
)
from capellacollab.settings.modelsources.t4c import crud
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CInstance,
    DatabaseT4CInstance,
    PatchT4CInstance,
    T4CInstance,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    T4CInstanceWithRepositories,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    router as repositories_router,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.users.models import Role

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)


@router.get("/", response_model=list[T4CInstance])
def list_t4c_settings(
    db: Session = Depends(get_db),
) -> list[DatabaseT4CInstance]:
    return crud.get_all_t4c_instances(db)


@router.get(
    "/{t4c_instance_id}",
    response_model=T4CInstance,
)
def get_t4c_instance(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
) -> DatabaseT4CInstance:
    return instance


@router.post(
    "/",
    response_model=T4CInstance,
)
def create_t4c_instance(
    body: CreateT4CInstance,
    db: Session = Depends(get_db),
) -> DatabaseT4CInstance:
    version = get_version_by_id_or_raise(db, body.version_id)
    instance = DatabaseT4CInstance(**body.dict())
    instance.version = version
    return crud.create_t4c_instance(instance, db)


@router.patch(
    "/{t4c_instance_id}",
    response_model=T4CInstance,
)
def edit_t4c_instance(
    body: PatchT4CInstance,
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    db: Session = Depends(get_db),
) -> DatabaseT4CInstance:
    for key in body.dict():
        if value := body.__getattribute__(key):
            instance.__setattr__(key, value)
    return crud.update_t4c_instance(instance, db)


router.include_router(
    repositories_router, prefix="/{t4c_instance_id}/repositories"
)
