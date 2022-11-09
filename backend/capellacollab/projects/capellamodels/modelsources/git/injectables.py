# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DatabaseGitModel,
)

from . import crud


def get_existing_git_model(
    git_model_id: int,
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseGitModel:
    git_model = crud.get_gitmodel_by_id(db, git_model_id)

    if git_model.model_id == capella_model.id:
        return git_model

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "git_model_not_exists_on_project_and_model",
            "reason": f"The git model ({git_model_id}) does not exists on the capella model for the project",
        },
    )


def get_existing_primary_git_model(
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseGitModel:
    primary_git_model = crud.get_primary_gitmodel_of_capellamodel(
        db, capella_model.id
    )

    if primary_git_model:
        return primary_git_model

    raise HTTPException(
        status_code=500,
        detail={
            "err_code": "no_git_model",
            "reason": "No git model is assigned to your project. Please ask a project lead to assign a git model.",
        },
    )
