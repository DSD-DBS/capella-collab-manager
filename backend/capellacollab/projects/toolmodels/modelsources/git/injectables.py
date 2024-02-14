# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)

from . import crud
from .handler import factory, handler


def get_existing_git_model(
    git_model_id: int,
    capella_model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> git_models.DatabaseGitModel:
    git_model = crud.get_git_model_by_id(db, git_model_id)
    if git_model and git_model.model.id == capella_model.id:
        return git_model

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "err_code": "GIT_MODEL_NOT_EXISTING",
            "reason": f"The git model ({git_model_id}) does not exists on the capella model for the project",
        },
    )


def get_existing_primary_git_model(
    capella_model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> git_models.DatabaseGitModel:
    primary_git_model = crud.get_primary_git_model_of_capellamodel(
        db, capella_model.id
    )

    if primary_git_model:
        return primary_git_model

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "err_code": "no_git_model",
            "reason": "No git model is assigned to your project. Please ask a project lead to assign a git model.",
        },
    )


def get_git_handler(
    git_model: git_models.DatabaseGitModel = fastapi.Depends(
        get_existing_primary_git_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> handler.GitHandler:
    return factory.GitHandlerFactory.create_git_handler(db, git_model)
