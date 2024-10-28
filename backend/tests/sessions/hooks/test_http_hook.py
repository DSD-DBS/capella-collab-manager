# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import pytest

from capellacollab.sessions import auth as sessions_auth
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import http
from capellacollab.sessions.hooks import interface as sessions_hooks_interface
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


def test_http_hook(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    logger: logging.LoggerAdapter,
):
    session.environment = {
        "TEST": "test",
        "CAPELLACOLLAB_SESSION_TOKEN": "test",
    }
    connection_method = tools_models.HTTPConnectionMethod(
        redirect_url="http://localhost:8000/{TEST}",
        cookies={"test": "{TEST}"},
    )
    result = http.HTTPIntegration().session_connection_hook(
        db_session=session,
        user=user,
        connection_method=connection_method,
        logger=logger,
    )

    assert result["cookies"]["test"] == "test"
    assert result["redirect_url"] == "http://localhost:8000/test"
    assert not result["warnings"]


def test_skip_http_hook_if_guacamole(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    logger: logging.LoggerAdapter,
):
    result = http.HTTPIntegration().session_connection_hook(
        db_session=session,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        user=user,
        logger=logger,
    )
    assert result == sessions_hooks_interface.SessionConnectionHookResult()


def test_fail_derive_redirect_url(
    session: sessions_models.DatabaseSession,
    user: users_models.DatabaseUser,
    logger: logging.LoggerAdapter,
):
    session.environment = {"TEST": "test"}
    connection_method = tools_models.HTTPConnectionMethod(
        redirect_url="http://localhost:8000/{TEST2}"
    )
    result = http.HTTPIntegration().session_connection_hook(
        db_session=session,
        connection_method=connection_method,
        user=user,
        logger=logger,
    )

    assert len(result["warnings"]) == 1
    assert result["warnings"][0].err_code == "REDIRECT_URL_DERIVATION_FAILED"
