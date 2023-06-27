# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import json

from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)


def get_environment(
    git_model: git_models.DatabaseGitModel,
    t4c_model: t4c_models.DatabaseT4CModel,
    t4c_username: str,
    t4c_password: str,
    include_commit_history: bool = False,
) -> dict[str, str]:
    env = {
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
        "INCLUDE_COMMIT_HISTORY": json.dumps(include_commit_history),
    }

    if http_port := t4c_model.repository.instance.http_port:
        env = env | {
            "HTTP_LOGIN": t4c_model.repository.instance.username,
            "HTTP_PASSWORD": t4c_model.repository.instance.password,
            "HTTP_PORT": str(http_port),
        }
    else:
        env = env | {
            "T4C_CDO_PORT": str(t4c_model.repository.instance.cdo_port)
        }

    return env
