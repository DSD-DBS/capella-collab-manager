# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.sessions import models as sessions_models

from . import interface


class ResolvedSessionProvisioning(t.TypedDict):
    entry: sessions_models.SessionProvisioningRequest
    model: toolmodels_models.DatabaseToolModel
    project: projects_models.DatabaseProject
    git_model: git_models.DatabaseGitModel


class ProjectScopeHook(interface.HookRegistration):
    """Makes sure to start the session with the correct workspace."""

    @classmethod
    def configuration_hook(
        cls,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        environment = {}

        if (
            request.session_type == sessions_models.SessionType.PERSISTENT
            and request.project_scope
        ):
            environment["WORKSPACE_DIR"] = str(
                pathlib.PurePosixPath("/workspace")
                / request.project_scope.slug
                / ("tool-" + str(request.tool_version.tool_id))
            )

        return interface.ConfigurationHookResult(environment=environment)
