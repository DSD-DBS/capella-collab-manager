# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import pytest

from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import authentication
from capellacollab.users import models as users_models


def test_pre_authentication_hook(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    logger: logging.LoggerAdapter,
    monkeypatch: pytest.MonkeyPatch,
):
    private_key = sessions_auth.generate_private_key()
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY", private_key)

    result = authentication.PreAuthenticationHook().session_connection_hook(
        db_session=session,
        user=user,
        logger=logger,
    )

    assert "ccm_session_token" in result["cookies"]
