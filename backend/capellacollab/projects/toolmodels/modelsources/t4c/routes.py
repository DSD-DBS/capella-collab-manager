# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import capellacollab.core.database as database
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
)
from capellacollab.projects.toolmodels.backups import crud as backups_crud
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c import crud
from capellacollab.projects.toolmodels.modelsources.t4c.injectables import (
    get_existing_t4c_model,
)
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    SubmitT4CModel,
    T4CModel,
)
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    get_existing_t4c_repository,
)
from capellacollab.users.models import Role

router = APIRouter(
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)


@router.get(
    "",
    response_model=list[T4CModel],
)
def list_t4c_models(
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db_session: Session = Depends(database.get_db),
) -> list[DatabaseT4CModel]:
    return crud.get_t4c_models_for_tool_model(db_session, model)


@router.get(
    "/{t4c_model_id}",
    response_model=T4CModel,
)
def get_t4c_model(
    t4c_model: DatabaseT4CModel = Depends(get_existing_t4c_model),
) -> DatabaseT4CModel:
    return t4c_model


@router.post(
    "",
    response_model=T4CModel,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_t4c_model(
    body: SubmitT4CModel,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db_session: Session = Depends(database.get_db),
):
    instance = get_existing_instance(body.t4c_instance_id, db_session)
    repository = get_existing_t4c_repository(
        body.t4c_repository_id, db_session, instance
    )
    try:
        return crud.create_t4c_model(db_session, model, repository, body.name)
    except IntegrityError as exc:
        raise HTTPException(
            409,
            {"reason": "The model has been added already."},
        ) from exc


@router.patch(
    "/{t4c_model_id}",
    response_model=T4CModel,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def edit_t4c_model(
    body: SubmitT4CModel,
    t4c_model: DatabaseT4CModel = Depends(get_existing_t4c_model),
    db_session: Session = Depends(database.get_db),
):
    return crud.patch_t4c_model(db_session, t4c_model, body)


@router.delete(
    "/{t4c_model_id}",
    status_code=204,
    dependencies=[
        Depends(ProjectRoleVerification(required_role=ProjectUserRole.MANAGER))
    ],
)
def delete_t4c_model(
    t4c_model: DatabaseT4CModel = Depends(get_existing_t4c_model),
    db: Session = Depends(database.get_db),
):
    if backups_crud.get_pipelines_for_t4c_model(db, t4c_model):
        raise HTTPException(
            status_code=409,
            detail={
                "err_code": "git_model_used_for_backup",
                "reason": "The git model can't be deleted: it's used for backup jobs",
            },
        )

    crud.delete_t4c_model(db, t4c_model)
