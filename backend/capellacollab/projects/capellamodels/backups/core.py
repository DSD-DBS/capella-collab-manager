# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

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
    include_commit_history: bool,
):
    return {
        "GIT_REPO_URL": gitmodel.path,
        "GIT_REPO_BRANCH": gitmodel.revision,
        "GIT_USERNAME": gitmodel.username,
        "GIT_PASSWORD": gitmodel.password,
        "T4C_REPO_HOST": t4cmodel.repository.instance.host,
        "T4C_REPO_PORT": t4cmodel.repository.instance.port,
        "T4C_CDO_PORT": "CDOPORT",  # FIXME
        "T4C_REPO_NAME": t4cmodel.repository.name,
        "T4C_PROJECT_NAME": t4cmodel.name,
        "T4C_USERNAME": t4cmodel.repository.instance.username,
        "T4C_PASSWORD": t4cmodel.repository.instance.password,
        "LOG_LEVEL": "INFO",
        "INCLUDE_COMMIT_HISTORY": json.dumps(include_commit_history),
    }
