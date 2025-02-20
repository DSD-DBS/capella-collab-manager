# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.sessions.hooks import interface as sessions_hooks_interface
from capellacollab.sessions.hooks import session_token
from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as tokens_crud


def test_session_token_hook_lifecycle(
    user: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    configuration_hook_request: sessions_hooks_interface.ConfigurationHookRequest,
    pre_session_termination_hook_request: sessions_hooks_interface.PreSessionTerminationHookRequest,
    db: orm.Session,
):
    configuration_hook_request.project_scope = project
    result = session_token.SessionTokenIntegration().configuration_hook(
        configuration_hook_request
    )

    session_token_id = result["config"]["session_token_id"]
    assert isinstance(session_token_id, int)
    assert result["config"]["session_token_id"]
    assert result["environment"]["CAPELLACOLLAB_SESSION_API_TOKEN"]

    assert tokens_crud.get_token_by_user_and_id(db, user.id, session_token_id)

    pre_session_termination_hook_request.session.config["session_token_id"] = (
        str(session_token_id)
    )

    session_token.SessionTokenIntegration().pre_session_termination_hook(
        pre_session_termination_hook_request
    )

    assert not tokens_crud.get_token_by_user_and_id(
        db, user.id, session_token_id
    )


def test_termination_with_revoked_token(
    pre_session_termination_hook_request: sessions_hooks_interface.PreSessionTerminationHookRequest,
):
    """Test that a session can be terminated if the PAT was already revoked"""

    pre_session_termination_hook_request.session.config["session_token_id"] = (
        "1"
    )

    session_token.SessionTokenIntegration().pre_session_termination_hook(
        pre_session_termination_hook_request
    )
