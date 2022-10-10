# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import HTTPException

import capellacollab.extensions.modelsources.git.crud as crud_git_models
import capellacollab.projects.models as crud_git_models


def verify_gitmodel_permission(
    project: str, model_id: str, git_model_id: int, db
):

    # FIXME: Validate if the gitmodel is part of a specific model and the model is part of the project
    if (
        crud_git_models.get_gitmodel_by_id(db, git_model_id).model_id
        != model_id
    ):
        raise HTTPException(
            status_code=403,
            detail="The Git repository is not part of the specified model and project!",
        )
