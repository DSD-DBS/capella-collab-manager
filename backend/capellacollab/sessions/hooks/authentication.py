# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import jwt

from capellacollab.users import models as users_models

from .. import auth as sessions_auth
from .. import models as sessions_models
from . import interface


class PreAuthenticationHook(interface.HookRegistration):
    def session_connection_hook(
        self,
        request: interface.SessionConnectionHookRequest,
    ) -> interface.SessionConnectionHookResult:
        """Issue pre-authentication tokens for sessions"""

        return interface.SessionConnectionHookResult(
            cookies={
                "ccm_session_token": self._issue_session_token(
                    request.user, request.db_session
                )
            }
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
