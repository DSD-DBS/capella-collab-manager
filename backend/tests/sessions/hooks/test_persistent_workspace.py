# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.hooks import persistent_workspace
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


def test_persistent_workspace_mounting_not_allowed(
    tool: tools_models.DatabaseTool,
    user: users_models.DatabaseUser,
):
    tool.config.persistent_workspaces.mounting_enabled = False

    with pytest.raises(sessions_exceptions.WorkspaceMountingNotAllowedError):
        persistent_workspace.PersistentWorkspaceHook().configuration_hook(
            operator=operators.KubernetesOperator(),
            user=user,
            session_type=sessions_models.SessionType.PERSISTENT,
            tool=tool,
        )
