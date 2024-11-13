# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import session_preparation


def test_session_preparation_hook(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that the session preparation hook registers a shared volume"""
    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )
    result = session_preparation.GitRepositoryCloningHook().configuration_hook(
        configuration_hook_request
    )

    assert len(result["volumes"]) == 1
    assert len(result["init_volumes"]) == 1
    assert result["volumes"][0] == result["init_volumes"][0]
    assert result["volumes"][0].name == "nxylxqbmfqwvswlqlcbsirvrt-models"


def test_session_preparation_hook_with_persistent_session(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that the session preparation hook doesn't do anything for persistent sessions"""

    result = session_preparation.GitRepositoryCloningHook().configuration_hook(
        configuration_hook_request
    )

    assert result == hooks_interface.ConfigurationHookResult()
