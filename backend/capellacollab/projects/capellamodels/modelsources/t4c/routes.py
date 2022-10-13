# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import capellacollab.core.database as database
import capellacollab.projects.capellamodels.modelsources.t4c.crud as database_projects
from capellacollab.core.authentication.database import (
    verify_admin,
    verify_project_role,
)
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.extensions.modelsources.t4c import crud
from capellacollab.extensions.modelsources.t4c.injectables import (
    load_project_model,
)
from capellacollab.extensions.modelsources.t4c.models import (
    CreateT4CModel,
    T4CModel,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.models import DatabaseProject
from capellacollab.settings.modelsources.t4c.injectables import load_instance
from capellacollab.settings.modelsources.t4c.repositories.models import (
    T4CRepositoryWithModels,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    load_instance_repository,
)

router = APIRouter()


@router.get(
    "/",
    responses=AUTHENTICATION_RESPONSES,
    response_model=list[T4CModel],
)
def list_t4c_models(
    t4c_instance_id: int,
    t4c_repository_id: int,
    db: Session = Depends(database.get_db),
    token: JWTBearer = Depends(JWTBearer()),
):
    verify_admin(token, db)
    instance = load_instance(t4c_instance_id, db)
    repository = load_instance_repository(t4c_repository_id, db, instance)[1]
    return T4CRepositoryWithModels.from_orm(repository).models


@router.post(
    "/",
)
def create_t4c_model(
    body: CreateT4CModel,
    project_model: tuple[DatabaseProject, DatabaseCapellaModel] = Depends(
        load_project_model
    ),
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    instance = load_instance(body.t4c_instance_id, db)
    repository = load_instance_repository(
        body.t4c_repository_id, db, instance
    )[1]
    try:
        return crud.create_t4c_model(
            db, project_model[1], repository, body.name
        )
    except IntegrityError:
        raise HTTPException(
            409,
            {
                "reason": f"A model named {body.name} already exists in the repository {repository.name}."
            },
        )
