# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import models as core_models
from capellacollab.settings.modelsources.t4c import (
    injectables as settings_t4c_injectables,
)
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)

from . import crud, injectables, interface, models

router = fastapi.APIRouter()
log = logging.getLogger(__name__)

T4CRepositoriesResponseModel: t.TypeAlias = core_models.PayloadResponseModel[
    list[models.T4CRepository]
]


@router.get("", response_model=T4CRepositoriesResponseModel)
def list_t4c_repositories(
    db: orm.Session = fastapi.Depends(database.get_db),
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
) -> T4CRepositoriesResponseModel:
    repositories = models.T4CInstanceWithRepositories.model_validate(
        instance
    ).repositories

    try:
        server_repositories = interface.list_repositories(instance)
    except requests.RequestException as e:
        for repo in repositories:
            repo.status = models.T4CRepositoryStatus.INSTANCE_UNREACHABLE
        log.error("TeamForCapella server not reachable", exc_info=True)

        return T4CRepositoriesResponseModel(
            payload=repositories,
            warnings=[
                core_models.Message(
                    title="TeamForCapella server not reachable.",
                    reason="We will only show a representation of our database.",
                    technical=f"TeamForCapella not reachable with exception {e}",
                )
            ],
        )

    repositories = sync_db_with_server_repositories(
        db=db,
        db_repos=repositories,
        server_repos=server_repositories,
        instance=instance,
    )

    return T4CRepositoriesResponseModel(payload=repositories)


@router.post("", response_model=models.T4CRepository)
def create_t4c_repository(
    body: models.CreateT4CRepository,
    db: orm.Session = fastapi.Depends(database.get_db),
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
) -> models.T4CRepository:
    if crud.exist_repo_for_name_and_instance(db, body.name, instance):
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": f"Repository {body.name} of instance {instance.name} already exists.",
            },
        )

    repo = models.T4CRepository.model_validate(
        crud.create_t4c_repository(
            db=db, repo_name=body.name, instance=instance
        )
    )

    try:
        repo.status = models.T4CRepositoryStatus(
            interface.create_repository(instance, repo.name)["repository"][
                "status"
            ]
        )
    except requests.RequestException:
        repo.status = models.T4CRepositoryStatus.INSTANCE_UNREACHABLE

    return repo


@router.delete(
    "/{t4c_repository_id}",
    response_model=core_models.ResponseModel | None,
)
def delete_t4c_repository(
    response: fastapi.Response,
    db: orm.Session = fastapi.Depends(database.get_db),
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
    repository: models.DatabaseT4CRepository = fastapi.Depends(
        injectables.get_existing_t4c_repository
    ),
) -> core_models.ResponseModel | None:
    crud.delete_4c_repository(db, repository)
    try:
        interface.delete_repository(instance, repository.name)
    except (fastapi.HTTPException, requests.RequestException) as e:
        log.error("Repository deletion failed partially", exc_info=True)
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        if isinstance(e, fastapi.HTTPException):
            reason: tuple[str, ...] = (
                "The TeamForCapella returned an error when deleting the repository.",
                "We deleted it the repository our database. When the connection is successful, we'll synchronize the repositories again.",
            )
            technical = f"TeamForCapella returned status code {e.status_code}"
        else:
            reason = (
                "The TeamForCapella server is not reachable.",
                "We deleted the repository from our database.",
                "During the next connection attempt, we'll synchronize the repository again.",
            )
            technical = f"TeamForCapella not reachable with exception {e}"

        return create_single_warning_response_model(
            title="Repository deletion failed partially.",
            reason=reason,
            technical=technical,
        )

    response.status_code = status.HTTP_204_NO_CONTENT
    return None


@router.post(
    "/{t4c_repository_id}/start", status_code=status.HTTP_204_NO_CONTENT
)
def start_t4c_repository(
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
    repository: models.DatabaseT4CRepository = fastapi.Depends(
        injectables.get_existing_t4c_repository
    ),
):
    interface.start_repository(instance, repository.name)


@router.post(
    "/{t4c_repository_id}/stop", status_code=status.HTTP_204_NO_CONTENT
)
def stop_t4c_repository(
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
    repository: models.DatabaseT4CRepository = fastapi.Depends(
        injectables.get_existing_t4c_repository
    ),
):
    interface.stop_repository(instance, repository.name)


@router.post(
    "/{t4c_repository_id}/recreate", status_code=status.HTTP_204_NO_CONTENT
)
def recreate_t4c_repository(
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
    repository: models.DatabaseT4CRepository = fastapi.Depends(
        injectables.get_existing_t4c_repository
    ),
):
    interface.create_repository(instance, repository.name)


def sync_db_with_server_repositories(
    db: orm.Session,
    db_repos: list[models.T4CRepository],
    server_repos: dict,
    instance: settings_t4c_models.DatabaseT4CInstance,
) -> list[models.T4CRepository]:
    """
    Synchronize the repository list in the database with the repository list from a server.

    This function performs three main operations:
    - For repositories that exist both in the database and on the server, it updates the status of the database repository to match the server's status.
    - For repositories that exist in the database but not on the server, it sets the database repository status to NOT_FOUND.
    - For repositories that exist on the server but not in the database, it creates a new repository entry in the database with the status from the server.

    Parameters
    ----------
    db : Session
        The database session.
    db_repos : list[T4CRepository]
        The list of repository objects from the database.
    server_repos : dict
        The dictionary of repository data from the server, where the keys are repository names and the values are repository data.
    instance : DatabaseT4CInstance
        The database instance associated with the repositories.

    Returns
    -------
    list[T4CRepository]
        The sorted list of updated database repository objects, sorted by repository id.
    """

    db_repos_dict = {repo.name: repo for repo in db_repos}
    server_repos_dict = {repo["name"]: repo for repo in server_repos}

    db_repos_names = set(db_repos_dict.keys())
    server_repos_names = set(server_repos_dict.keys())

    db_and_server_repo_names = server_repos_names & db_repos_names
    for repo_name in db_and_server_repo_names:
        db_repos_dict[repo_name].status = server_repos_dict[repo_name][
            "status"
        ]

    db_not_server_repo_names = db_repos_names - server_repos_names
    for repo_name in db_not_server_repo_names:
        db_repos_dict[repo_name].status = models.T4CRepositoryStatus.NOT_FOUND

    server_not_db_repo_names = server_repos_names - db_repos_names
    for repo_name in server_not_db_repo_names:
        repo = models.T4CRepository.model_validate(
            crud.create_t4c_repository(
                db=db, repo_name=repo_name, instance=instance
            )
        )
        repo.status = server_repos_dict[repo.name]["status"]
        db_repos_dict[repo_name] = repo

    return sorted(db_repos_dict.values(), key=lambda repo: repo.id)


def create_single_warning_response_model(
    title: str, reason: str | tuple[str, ...], technical: str
) -> core_models.ResponseModel:
    return core_models.ResponseModel(
        errors=[],
        warnings=[
            core_models.Message(
                title=title,
                reason=reason,
                technical=technical,
            )
        ],
    )
