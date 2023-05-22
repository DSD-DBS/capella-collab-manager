# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.crud as git_crud
import capellacollab.projects.toolmodels.modelsources.git.gitlab.interface as gitlab_interface

from . import models


def check_pipeline_health(
    db: orm.Session,
    model: toolmodels_models.DatabaseCapellaModel,
    job_name: str,
) -> models.ModelArtifactStatus:
    primary_git_model = git_crud.get_primary_git_model_of_capellamodel(
        db, model.id
    )
    if not primary_git_model:
        return models.ModelArtifactStatus.UNCONFIGURED

    try:
        gitlab_interface.get_last_job_run_id_for_git_model(
            db, job_name, primary_git_model
        )
    except fastapi.HTTPException as e:
        match e.detail.get("err_code", ""):
            case (
                "NO_SUCCESSFUL_JOB"
                | "NO_MATCHING_GIT_INSTANCE"
                | "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
                | "GITLAB_ACCESS_DENIED"
                | "PROJECT_NOT_FOUND"
            ):
                return models.ModelArtifactStatus.FAILURE
            case "INSTANCE_IS_NO_GITLAB_INSTANCE":
                return models.ModelArtifactStatus.UNSUPPORTED
            case "PIPELINE_JOB_NOT_FOUND":
                return models.ModelArtifactStatus.UNCONFIGURED
            case _:
                return models.ModelArtifactStatus.FAILURE
    except:  # pylint: disable=bare-except
        return models.ModelArtifactStatus.FAILURE

    return models.ModelArtifactStatus.SUCCESS
