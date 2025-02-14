# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)

from . import crud, exceptions
from .handler import factory, handler


def get_existing_git_model(
    git_model_id: int,
    capella_model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> git_models.DatabaseGitModel:
    git_model = crud.get_git_model_by_id(db, git_model_id)
    if git_model and git_model.model.id == capella_model.id:
        return git_model

    raise exceptions.GitRepositoryNotFoundError(
        git_model_id, capella_model.slug
    )


def get_existing_primary_git_model(
    tool_model: t.Annotated[toolmodels_models.DatabaseToolModel, fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> git_models.DatabaseGitModel:
    primary_git_model = crud.get_primary_git_model_of_capellamodel(
        db, tool_model.id
    )

    if primary_git_model:
        return primary_git_model

    raise exceptions.NoGitRepositoryAssignedToModelError(tool_model.slug)


async def get_git_handler(
    git_model: t.Annotated[git_models.DatabaseGitModel, fastapi.Depends(
        get_existing_primary_git_model
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> handler.GitHandler:
    return await factory.GitHandlerFactory.create_git_handler(db, git_model)
