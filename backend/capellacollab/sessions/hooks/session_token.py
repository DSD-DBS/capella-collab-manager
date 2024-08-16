# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

from sqlalchemy import orm

from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as tokens_crud

from .. import models as sessions_models
from . import interface


class SessionTokenIntegration(interface.HookRegistration):
    """Create a PAT valid for the duration of the session."""

    def configuration_hook(  # type: ignore
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        session_id: str,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        token, password = tokens_crud.create_token(
            db,
            user,
            f"Session token for session {session_id}. Will be revoked when the session is terminated.",
            datetime.date.today()
            + datetime.timedelta(
                days=1
            ),  # Maximum duration is until end of the next day.
            "SessionTokenIssuer",
        )

        return interface.ConfigurationHookResult(
            environment={"CAPELLACOLLAB_SESSION_TOKEN": password},
            config={"session_token_id": token.id},
        )

    def pre_session_termination_hook(  # type: ignore
        self,
        db: orm.Session,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ) -> interface.PreSessionTerminationHookResult:
        token_id = session.config.get("session_token_id")
        if not token_id:
            return interface.PreSessionTerminationHookResult()

        token = tokens_crud.get_token_by_user_and_id(
            db, session.owner.id, int(token_id)
        )
        if not token:
            return interface.PreSessionTerminationHookResult()

        tokens_crud.delete_token(db, token)
        return interface.PreSessionTerminationHookResult()
