# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException

from t4cclient.core.database import get_db
from t4cclient.extensions.backups import jenkins

from . import git_models as git_models_auth


def verify_jenkins_permission(
    repository: str, pipeline_name: str, git_model_id: int, db
):
    git_models_auth.verify_gitmodel_permission(repository, git_model_id, db)
    if (
        jenkins.crud.get_pipeline_of_model(db, git_model_id).name
        != pipeline_name
    ):
        raise HTTPException(
            status_code=403,
            detail="The Pipeline Name does not match with the connected Git Model!",
        )
