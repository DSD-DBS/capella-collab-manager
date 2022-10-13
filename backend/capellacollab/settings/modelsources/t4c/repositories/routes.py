# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import APIRouter, Depends, HTTPException, Response, status
from requests.exceptions import RequestException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.core.models import Message, ResponseModel
from capellacollab.settings.modelsources.t4c.injectables import load_instance
from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CRepository,
    DatabaseT4CInstance,
    Status,
    T4CInstanceWithRepositories,
    T4CRepositories,
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
    t4c_repository_id: int,
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(load_instance),
) -> tuple[DatabaseT4CInstance, DatabaseT4CRepository]:
    try:
        repository = crud.get_t4c_repository(t4c_repository_id, db)
    except NoResultFound as e:
        raise HTTPException(
            404,
            {
                "reason": f"Repository with id {t4c_repository_id} was not found."
            },
        ) from e
    if repository.instance != instance:
        raise HTTPException(
            409,
            {
                "reason": f"Repository {repository.name} is not part of the instance {instance.name}."
            },
        )
    return repository


@router.get(
    "/",
    responses=AUTHENTICATION_RESPONSES,
    response_model=T4CRepositories,
)
def list_t4c_repositories(
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
    instance: DatabaseT4CInstance = Depends(load_instance),
) -> T4CRepositories:
    verify_admin(token, db)
    db_repositories = T4CInstanceWithRepositories.from_orm(
        instance
    ).repositories
    try:
        server_repositories = interface.list_repositories(instance)
    except RequestException:
        for i in range(len(db_repositories)):
            db_repositories[i].status = Status.INSTANCE_UNREACHABLE
        return T4CRepositories(
            payload=db_repositories,
            warnings=[
                Message(
                    title="TeamForCapella server not reachable.",
                    reason=(
                        "We will only show a representation of our database."
                    ),
                )
            ],
        )

    server_repositories_dict = {
        repo["name"]: repo for repo in server_repositories
    }
    db_repositories_dict = {repo.name: repo for repo in db_repositories}

    server_repositories_names = set(server_repositories_dict.keys())
    db_repositories_names = set(db_repositories_dict.keys())

    # Repository exists on the server and in the database
    for repo in server_repositories_names & db_repositories_names:
        db_repositories_dict[repo].status = server_repositories_dict[repo][
            "status"
        ]

    # Repository exists in the database, but not on the server
    for repo in db_repositories_names - server_repositories_names:
        db_repositories_dict[repo].status = Status.NOT_FOUND

    # Repository exists on the server, but not in the database
    for repo in server_repositories_names - db_repositories_names:
        new_repo = CreateT4CRepository(name=repo)
        db_repo = T4CRepository.from_orm(
            crud.create_t4c_repository(new_repo, instance, db)
        )
        db_repo.status = db_repositories_dict[repo]["status"]
        db_repositories_dict[repo] = db_repo

    return T4CRepositories(
        payload=sorted(db_repositories_dict.values(), key=lambda r: r.id)
    )


@router.post(
    "/", responses=AUTHENTICATION_RESPONSES, response_model=T4CRepository
)
def create_t4c_repository(
    body: CreateT4CRepository,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
    instance: DatabaseT4CInstance = Depends(load_instance),
) -> T4CRepository:
    verify_admin(token, db)
    try:
        new_repo = T4CRepository.from_orm(
            crud.create_t4c_repository(body, instance, db)
        )
    except IntegrityError as e:
        raise HTTPException(
            409,
            {
                "reason": f"Repository {body.name} of instance {instance.name} already exists.",
            },
        ) from e
    try:
        new_repo.status = Status(
            interface.create_repository(instance, new_repo.name)["repository"][
                "status"
            ]
        )
    except RequestException:
        new_repo.status = Status.INSTANCE_UNREACHABLE
    return new_repo


@router.delete(
    "/{t4c_repository_id}",
    responses=AUTHENTICATION_RESPONSES,
    response_model=t.Optional[ResponseModel],
)
def delete_t4c_repository(
    response: Response,
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(load_instance),
    repository: DatabaseT4CRepository = Depends(load_instance_repository),
) -> None:
    verify_admin(token, db)
    crud.delete_4c_repository(repository, db)
    try:
        interface.delete_repository(instance, repository.name)
    except HTTPException as e:
        response.status_code = status.HTTP_207_MULTI_STATUS
        return ResponseModel(
            warnings=[
                Message(
                    title="Repository deletion failed partially.",
                    reason=(
                        "The TeamForCapella returned an error when deleting the repository.",
                        "We deleted it the repository our database. When the connection is successful, we'll synchronize the repositories again.",
                    ),
                    technical=f"TeamForCapella returned status code {e.status_code}",
                )
            ]
        )
    except RequestException as e:
        response.status_code = status.HTTP_207_MULTI_STATUS
        return ResponseModel(
            warnings=[
                Message(
                    title="Repository deletion failed partially.",
                    reason=(
                        "The TeamForCapella server is not reachable.",
                        "We deleted the repository from our database.",
                        "During the next connection attempt, we'll synchronize the repository again.",
                    ),
                    technical=f"TeamForCapella not reachable with exception {e}",
                )
            ]
        )
    response.status_code = status.HTTP_204_NO_CONTENT
    return None


@router.post(
    "/{t4c_repository_id}/start",
    responses=AUTHENTICATION_RESPONSES,
    status_code=204,
)
def start_t4c_repository(
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(load_instance),
    repository: DatabaseT4CRepository = Depends(load_instance_repository),
) -> None:
    verify_admin(token, db)
    interface.start_repository(instance, repository.name)
    return None


@router.post(
    "/{t4c_repository_id}/stop",
    responses=AUTHENTICATION_RESPONSES,
    status_code=204,
)
def stop_t4c_repository(
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(load_instance),
    repository: DatabaseT4CRepository = Depends(load_instance_repository),
) -> None:
    verify_admin(token, db)
    interface.stop_repository(instance, repository.name)
    return None


@router.post(
    "/{t4c_repository_id}/recreate",
    responses=AUTHENTICATION_RESPONSES,
    status_code=204,
)
def recreate_t4c_repository(
    token: JWTBearer = Depends(JWTBearer()),
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(load_instance),
    repository: DatabaseT4CRepository = Depends(load_instance_repository),
) -> None:
    verify_admin(token, db)
    interface.create_repository(instance, repository.name)
    return None
