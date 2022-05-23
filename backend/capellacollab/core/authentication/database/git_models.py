# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 3rd party:
from fastapi import HTTPException

# 1st party:
import capellacollab.extensions.modelsources.git.crud as crud_git_models


def verify_gitmodel_permission(repository: str, git_model_id: int, db):
    if (
        crud_git_models.get_model_by_id(db, repository, git_model_id).repository_name
        != repository
    ):
        raise HTTPException(
            status_code=403,
            detail="The Git Model is not part of the specified repository!",
        )
