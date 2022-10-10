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
    DatabaseT4CInstance,
    Status,
    T4CInstanceWithRepositories,
    T4CRepository,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    crud,
    interface,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)

router = APIRouter()


def load_instance_repository(
    instance_id: int, id_: int, db: Session = Depends(get_db)
) -> tuple[DatabaseT4CInstance, DatabaseT4CRepository]:
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
            409,
            {
                "reason": f"Repository {repository.name} is not part of the instance {instance.name}."
            },
        )
    return instance, repository


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
        instance = instance_crud.get_t4c_instance(instance_id, db)
    except NoResultFound:
        raise HTTPException(
            404, {"reason": f"Instance with id {instance_id} was not found."}
        )
    server_repositories = interface.list_repositories(instance)
    server_repositories.sort(key=lambda r: r["name"])
    db_repositories = T4CInstanceWithRepositories.from_orm(
        instance
    ).repositories
    db_repositories.sort(key=lambda r: r.name)

    i = j = 0
    while i < len(db_repositories) and j < len(server_repositories):
        if db_repositories[i].name < server_repositories[j]["name"]:
            i += 1
            continue
        if db_repositories[i].name > server_repositories[j]["name"]:
            j += 1
            continue
        db_repositories[i].status = server_repositories[j]["status"]
        del server_repositories[j]
        i += 1

    for repo in server_repositories:
        new_repo = CreateT4CRepository(name=repo["name"])
        db_repo = T4CRepository.from_orm(
            crud.create_t4c_repository(new_repo, instance, db)
        )
        db_repo.status = repo["status"]
        db_repositories.append(db_repo)

    for repo in [repo for repo in db_repositories if not repo.status]:
        interface.create_repository(instance, repo.name)
        repo.status = Status.ONLINE

    return sorted(db_repositories, key=lambda r: r.id)


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
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    objects: tuple[DatabaseT4CInstance, DatabaseT4CRepository] = Depends(
        load_instance_repository
    ),
) -> None:
    (instance, repository) = objects
    verify_admin(token, db)
    interface.delete_repository(instance, repository.name)
    crud.delete_4c_repository(repository, db)


@router.post(
    "/{id_}/start", responses=AUTHENTICATION_RESPONSES, status_code=204
)
def start_t4c_repository(
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    objects: tuple[DatabaseT4CInstance, DatabaseT4CRepository] = Depends(
        load_instance_repository
    ),
) -> None:
    verify_admin(token, db)
    (instance, repository) = objects
    interface.start_repository(instance, repository.name)


@router.post(
    "/{id_}/stop", responses=AUTHENTICATION_RESPONSES, status_code=204
)
def stop_t4c_repository(
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    objects: tuple[DatabaseT4CInstance, DatabaseT4CRepository] = Depends(
        load_instance_repository
    ),
) -> None:
    verify_admin(token, db)
    (instance, repository) = objects
    interface.stop_repository(instance, repository.name)
