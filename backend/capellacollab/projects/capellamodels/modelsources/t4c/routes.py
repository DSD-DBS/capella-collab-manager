# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

import capellacollab.core.database as database
from capellacollab.core.authentication.database import (
    ProjectRoleVerification,
    RoleVerification,
    verify_admin,
    verify_project_role,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.t4c import crud
from capellacollab.projects.capellamodels.modelsources.t4c.injectables import (
    get_existing_t4c_model,
)
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    ResponseT4CModel,
    SubmitT4CModel,
    T4CRepositoryWithModels,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.users.models import ProjectUserRole
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories.injectables import (
    get_optional_existing_instance_repository,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    get_existing_instance_repository,
)
from capellacollab.users.models import Role

router = APIRouter()


@router.get(
    "/",
    response_model=list[ResponseT4CModel],
)
def list_t4c_models(
    project: DatabaseProject = Depends(get_existing_project),
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    repository: t.Optional[DatabaseT4CRepository] = Depends(
        get_optional_existing_instance_repository
    ),
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
) -> DatabaseT4CModel:
    if not repository:
        ProjectRoleVerification(ProjectUserRole.USER)(project.slug, token, db)
        return model.t4c_models
    return repository.models


@router.get(
    "/{t4c_model_id}/",
    response_model=ResponseT4CModel,
    dependencies=[Depends(ProjectRoleVerification(ProjectUserRole.USER))],
)
def get_t4c_model(
    t4c_model: DatabaseT4CModel = Depends(get_existing_t4c_model),
) -> DatabaseT4CModel:
    return t4c_model


@router.post(
    "/",
    response_model=ResponseT4CModel,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_t4c_model(
    body: SubmitT4CModel,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(database.get_db),
):
    instance = get_existing_instance(body.t4c_instance_id, db)
    repository = get_existing_instance_repository(
        body.t4c_repository_id, db, instance
    )
    try:
        return crud.create_t4c_model(db, model, repository, body.name)
    except IntegrityError:
        raise HTTPException(
            409,
            {
                "reason": f"A model named {body.name} already exists in the repository {repository.name}."
            },
        )


@router.patch(
    "/{t4c_model_id}",
    response_model=ResponseT4CModel,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def edit_t4c_model(
    body: SubmitT4CModel,
    t4c_model: DatabaseT4CModel = Depends(get_existing_t4c_model),
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(database.get_db),
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    repository: DatabaseT4CRepository = Depends(
        get_existing_instance_repository
    ),
):
    if t4c_model.model != model:
        raise HTTPException(
            409,
            {
                "reason": f"The t4c model {t4c_model.name} is not part of the model {model.name}."
            },
        )
    t4c_model.repository = repository
    t4c_model.instance = instance
    return crud.patch_t4c_model(db, t4c_model, body)
