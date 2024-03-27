# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import session_preparation
from capellacollab.tools import models as tools_models


def test_session_preparation_hook(tool: tools_models.DatabaseTool):
    """Test that the session preparation hook registers a shared volume"""

    result = session_preparation.GitRepositoryCloningHook().configuration_hook(
        session_type=sessions_models.SessionType.READONLY,
        session_id="session-id",
        tool=tool,
    )

    assert len(result["volumes"]) == 1
    assert len(result["init_volumes"]) == 1
    assert result["volumes"][0] == result["init_volumes"][0]
    assert result["volumes"][0].name == "session-id-models"


def test_session_preparation_hook_with_persistent_session(
    tool: tools_models.DatabaseTool,
):
    """Test that the session preparation hook doesn't do anything for persistent sessions"""

    result = session_preparation.GitRepositoryCloningHook().configuration_hook(
        session_type=sessions_models.SessionType.PERSISTENT,
        session_id="session-id",
        tool=tool,
    )

    assert result == hooks_interface.ConfigurationHookResult()
