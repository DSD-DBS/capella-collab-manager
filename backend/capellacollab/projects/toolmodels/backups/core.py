# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging

import requests
from sqlalchemy import orm

from capellacollab.permissions import models as permissions_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    interface as t4c_repository_interface,
)

from . import crud, exceptions, interface, models

log = logging.getLogger(__name__)


def get_pipeline_labels(
    model: toolmodels_models.DatabaseToolModel,
) -> dict[str, str]:
    return {
        "app.capellacollab/projectSlug": model.project.slug,
        "app.capellacollab/projectID": str(model.project.id),
        "app.capellacollab/modelSlug": model.slug,
        "app.capellacollab/modelID": str(model.id),
    }


def get_environment(
    git_model: git_models.DatabaseGitModel,
    t4c_model: t4c_models.DatabaseT4CModel,
    t4c_username: str,
    t4c_password: str,
) -> dict[str, str]:
    return {
        "GIT_REPO_URL": git_model.path,
        "GIT_REPO_BRANCH": git_model.revision,
        "GIT_USERNAME": git_model.username,
        "GIT_PASSWORD": git_model.password,
        "T4C_REPO_HOST": t4c_model.repository.instance.host,
        "T4C_REPO_PORT": str(t4c_model.repository.instance.port),
        "T4C_REPO_NAME": t4c_model.repository.name,
        "T4C_PROJECT_NAME": t4c_model.name,
        "T4C_USERNAME": t4c_username,
        "T4C_PASSWORD": t4c_password,
        "LOG_LEVEL": "INFO",
    }


def delete_pipeline(
    db: orm.Session,
    pipeline: models.DatabasePipeline,
    force: bool,
    global_scope: permissions_models.GlobalScopes,
):
    try:
        t4c_repository_interface.remove_user_from_repository(
            pipeline.t4c_model.repository.instance,
            pipeline.t4c_model.repository.name,
            pipeline.t4c_username,
        )
    except requests.RequestException as e:
        log.exception(
            "Error during the deletion of user %s in t4c",
            pipeline.t4c_username,
        )

        if (
            not force
            or permissions_models.UserTokenVerb.UPDATE
            not in global_scope.admin.t4c_repositories
        ):
            raise exceptions.PipelineOperationFailedT4CServerUnreachable(
                exceptions.PipelineOperation.DELETE
            ) from e

    if pipeline.run_nightly:
        interface.unschedule_pipeline(pipeline)

    crud.delete_pipeline(db, pipeline)
