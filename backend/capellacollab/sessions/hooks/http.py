# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import jwt

from capellacollab.core import models as core_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import auth as sessions_auth
from .. import models as sessions_models
from .. import util as sessions_util
from . import interface


class HTTPIntegration(interface.HookRegistration):
    def session_connection_hook(
        self, request: interface.SessionConnectionHookRequest
    ) -> interface.SessionConnectionHookResult:
        ccm_session_token = self._issue_session_token(
            request.user, request.db_session
        )

        if not isinstance(
            request.connection_method, tools_models.HTTPConnectionMethod
        ):
            return interface.SessionConnectionHookResult(
                cookies={"ccm_session_token": ccm_session_token}
            )

        try:
            redirect_url = request.connection_method.redirect_url.format(
                **request.db_session.environment,
                CAPELLACOLLAB_SESSION_COOKIE=ccm_session_token,
            )
        except Exception:
            request.logger.exception("Error while formatting the redirect URL")
            return interface.SessionConnectionHookResult(
                cookies={"ccm_session_token": ccm_session_token},
                warnings=[
                    core_models.Message(
                        err_code="REDIRECT_URL_DERIVATION_FAILED",
                        title="Couldn't derive the redirect URL",
                        reason="Please check the backend logs for more information.",
                    )
                ],
            )

        cookies, warnings = sessions_util.resolve_environment_variables(
            request.logger,
            request.db_session.environment,
            request.connection_method.cookies,
        )

        return interface.SessionConnectionHookResult(
            redirect_url=redirect_url,
            cookies={**cookies, "ccm_session_token": ccm_session_token},
            warnings=warnings,
        )

    def _issue_session_token(
        self,
        user: users_models.DatabaseUser,
        db_session: sessions_models.DatabaseSession,
    ):
        assert sessions_auth.PRIVATE_KEY

        now = datetime.datetime.now(datetime.UTC)

        # The session token expires after 1 day.
        # In the rare case that a user works for more than 1 day
        # without a break, the user has to re-connect to the session.
        # Each connection attempt issues a new session token.
        expiration = now + datetime.timedelta(days=1)

        return jwt.encode(
            {
                "session": {"id": db_session.id},
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
                "iat": now,
                "exp": expiration,
            },
            sessions_auth.PRIVATE_KEY,
            algorithm="RS256",
        )
