# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

from capellacollab.projects.capellamodels.modelsources.git.models import (
    DatabaseGitModel,
)
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)


def get_environment(
    gitmodel: DatabaseGitModel,
    t4cmodel: DatabaseT4CModel,
    t4c_username: str,
    t4c_password: str,
    include_commit_history: bool,
) -> dict[str, str]:
    return {
        "GIT_REPO_URL": gitmodel.path,
        "GIT_REPO_BRANCH": gitmodel.revision,
        "GIT_USERNAME": gitmodel.username,
        "GIT_PASSWORD": gitmodel.password,
        "T4C_REPO_HOST": t4cmodel.repository.instance.host,
        "T4C_REPO_PORT": str(t4cmodel.repository.instance.port),
        "T4C_CDO_PORT": str(t4cmodel.repository.instance.cdo_port),
        "T4C_REPO_NAME": t4cmodel.repository.name,
        "T4C_PROJECT_NAME": t4cmodel.name,
        "T4C_USERNAME": t4c_username,
        "T4C_PASSWORD": t4c_password,
        "LOG_LEVEL": "INFO",
        "INCLUDE_COMMIT_HISTORY": json.dumps(include_commit_history),
    }
