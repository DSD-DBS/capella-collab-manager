# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.t4c import crud as instance_crud
from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CRepository,
    T4CInstanceWithRepositories,
    T4CRepository,
)
from capellacollab.settings.modelsources.t4c.repositories import crud

router = APIRouter()


@router.get(
    "/", responses=AUTHENTICATION_RESPONSES, response_model=list[T4CRepository]
)
def list_t4c_repositories(
    instance_id: int,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> list[T4CRepository]:
    verify_admin(token, db)
    try:
        return T4CInstanceWithRepositories.from_orm(
            instance_crud.get_t4c_instance(instance_id, db)
        ).repositories
    except NoResultFound:
        raise HTTPException(
            404, {"reason": f"Instance with id {instance_id} was not found."}
        )


@router.post(
    "/", responses=AUTHENTICATION_RESPONSES, response_model=T4CRepository
)
def create_t4c_repository(
    instance_id: int,
    body: CreateT4CRepository,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> T4CRepository:
    verify_admin(token, db)
    try:
        instance = instance_crud.get_t4c_instance(instance_id, db)
    except NoResultFound as e:
        raise HTTPException(
            404, {"reason": f"Instance with id {instance_id} was not found."}
        ) from e
    try:
        return T4CRepository.from_orm(
            crud.create_t4c_repository(body, instance, db)
        )
    except IntegrityError as e:
        raise HTTPException(
            409,
            {
                "reason": f"Repository {body.name} of instance {instance.name} already exists.",
            },
        ) from e


@router.delete(
    "/{id_}",
    responses=AUTHENTICATION_RESPONSES,
    status_code=204,
)
def delete_t4c_repository(
    instance_id: int,
    id_: int,
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
) -> t.NoReturn:
    verify_admin(token, db)
    try:
        instance = instance_crud.get_t4c_instance(instance_id, db)
    except NoResultFound as e:
        raise HTTPException(
            404, {"reason": f"Instance with id {instance_id} was not found."}
        ) from e
    try:
        repository = crud.get_t4c_repository(id_, db)
    except NoResultFound as e:
        raise HTTPException(
            404, {"reason": f"Repository with id {id_} was not found."}
        ) from e
    if repository.instance != instance:
        raise HTTPException(
            404,
            {
                "reason": f"Repository {repository.name} is not part of the instance {instance.name}."
            },
        )
    crud.delete_4c_repository(repository, db)
