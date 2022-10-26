# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

import capellacollab.core.database as database
from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
    get_existing_project,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.t4c import crud
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    ResponseT4CModel,
    SubmitT4CModel,
    T4CRepositoryWithModels,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.settings.modelsources.t4c.injectables import load_instance
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)
from capellacollab.settings.modelsources.t4c.repositories.routes import (
    load_instance_repository,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[ResponseT4CModel],
)
def list_t4c_models(
    db: Session = Depends(database.get_db),
    token: JWTBearer = Depends(JWTBearer()),
    model=Depends(get_existing_capella_model),
    repository: t.Optional[DatabaseT4CRepository] = Depends(
        load_instance_repository
    ),
):
    verify_admin(token, db)
    if not repository:
        return crud.get_all_t4c_models(db, model)
    return T4CRepositoryWithModels.from_orm(repository).models


@router.get("/{t4c_model_id}/", response_model=ResponseT4CModel)
def get_t4c_model(
    t4c_model_id: int,
    db: Session = Depends(database.get_db),
):
    return crud.get_t4c_model_by_id(db, t4c_model_id)


@router.post(
    "/",
)
def create_t4c_model(
    body: SubmitT4CModel,
    project: DatabaseProject = Depends(get_existing_project),
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    instance = load_instance(body.t4c_instance_id, db)
    repository = load_instance_repository(body.t4c_repository_id, db, instance)
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
)
def edit_t4c_model(
    t4c_model_id: int,
    body: SubmitT4CModel,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(database.get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    instance = load_instance(body.t4c_instance_id, db)
    repository = load_instance_repository(body.t4c_repository_id, db, instance)
    try:
        t4c_model = crud.get_t4c_model_by_id(db, t4c_model_id)
    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The model with the id {t4c_model_id} does not exist."
            },
        )
    if t4c_model.model != model:
        raise HTTPException(
            409,
            {
                "reason": f"The t4c model {t4c_model.name} is not part of the model {model.name}."
            },
        )
    for key in body.dict():
        if value := body.__getattribute__(key):
            t4c_model.__setattr__(key, value)
    return crud.patch_t4c_model(db, t4c_model, body)
