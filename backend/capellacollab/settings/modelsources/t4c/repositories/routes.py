# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import typing as t

from fastapi import APIRouter, Depends, HTTPException, Response, status
from requests.exceptions import RequestException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.core.models import Message, ResponseModel
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories import (
    crud,
    interface,
)

from .injectables import get_existing_t4c_repository
from .models import (
    CreateT4CRepository,
    DatabaseT4CRepository,
    T4CInstanceWithRepositories,
    T4CRepositories,
    T4CRepository,
    T4CRepositoryStatus,
)

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=T4CRepositories,
)
def list_t4c_repositories(
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
) -> T4CRepositories:
    db_repositories = T4CInstanceWithRepositories.from_orm(
        instance
    ).repositories
    try:
        server_repositories = interface.list_repositories(instance)
    except RequestException:
        for repo in db_repositories:
            repo.status = T4CRepositoryStatus.INSTANCE_UNREACHABLE
        log.debug("TeamForCapella server not reachable", exc_info=True)
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
        db_repositories_dict[repo].status = T4CRepositoryStatus.NOT_FOUND

    # Repository exists on the server, but not in the database
    for repo in server_repositories_names - db_repositories_names:
        new_repo = CreateT4CRepository(name=repo)
        db_repo = T4CRepository.from_orm(
            crud.create_t4c_repository(new_repo, instance, db)
        )
        db_repo.status = server_repositories_dict[repo]["status"]
        db_repositories_dict[repo] = db_repo

    return T4CRepositories(
        payload=sorted(db_repositories_dict.values(), key=lambda r: r.id)
    )


@router.post("/", response_model=T4CRepository)
def create_t4c_repository(
    body: CreateT4CRepository,
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
) -> T4CRepository:
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
        new_repo.status = T4CRepositoryStatus(
            interface.create_repository(instance, new_repo.name)["repository"][
                "status"
            ]
        )
    except RequestException:
        new_repo.status = T4CRepositoryStatus.INSTANCE_UNREACHABLE
    return new_repo


@router.delete(
    "/{t4c_repository_id}",
    response_model=t.Optional[ResponseModel],
)
def delete_t4c_repository(
    response: Response,
    db: Session = Depends(get_db),
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    repository: DatabaseT4CRepository = Depends(get_existing_t4c_repository),
) -> None | ResponseModel:
    crud.delete_4c_repository(repository, db)
    try:
        interface.delete_repository(instance, repository.name)
    except HTTPException as e:
        log.debug("Repository deletion failed partially", exc_info=True)
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
        log.debug("Repository deletion failed partially", exc_info=True)
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


@router.post(
    "/{t4c_repository_id}/start",
    status_code=204,
)
def start_t4c_repository(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    repository: DatabaseT4CRepository = Depends(get_existing_t4c_repository),
) -> None:
    interface.start_repository(instance, repository.name)


@router.post(
    "/{t4c_repository_id}/stop",
    status_code=204,
)
def stop_t4c_repository(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    repository: DatabaseT4CRepository = Depends(get_existing_t4c_repository),
) -> None:
    interface.stop_repository(instance, repository.name)


@router.post(
    "/{t4c_repository_id}/recreate",
    status_code=204,
)
def recreate_t4c_repository(
    instance: DatabaseT4CInstance = Depends(get_existing_instance),
    repository: DatabaseT4CRepository = Depends(get_existing_t4c_repository),
) -> None:
    interface.create_repository(instance, repository.name)
