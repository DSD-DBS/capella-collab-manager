# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.projects import models as projects_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import project_scope as project_scope_hook


def test_correct_workspace_with_project_scope(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    project: projects_models.DatabaseProject,
):
    """Test that the correct workspace is set with the project scope"""

    configuration_hook_request.project_scope = project
    result = project_scope_hook.ProjectScopeHook().configuration_hook(
        configuration_hook_request
    )

    assert (
        result["environment"]["WORKSPACE_DIR"]
        == f"/workspace/{project.slug}/tool-1"
    )
