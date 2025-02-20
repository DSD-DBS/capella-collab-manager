# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    crud as projects_permissions_crud,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.users.tokens import crud as tokens_crud

from . import interface


class SessionTokenIntegration(interface.HookRegistration):
    """Create a PAT valid for the duration of the session."""

    def configuration_hook(
        self,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        token, password = tokens_crud.create_token(
            db=request.db,
            scope=permissions_models.GlobalScopes(
                user=permissions_models.UserScopes(
                    sessions={permissions_models.UserTokenVerb.GET}
                )
            ),
            title=f"Session {request.session_id}",
            user=request.user,
            description=(
                "This PAT is managed by the Collaboration Manager."
                " It will be revoked when the session is terminated"
                " and is only valid for the duration of the session."
                " Manual deletion may lead to unexpected behavior."
            ),
            expiration_date=datetime.datetime.now(tz=datetime.UTC).date()
            + datetime.timedelta(
                days=2
            ),  # Maximum duration is until end of the next day.
            source="session automation",
        )

        if request.project_scope:
            projects_permissions_crud.create_personal_access_token_link(
                request.db,
                request.project_scope,
                token,
                projects_permissions_models.ProjectUserScopes(
                    diagram_cache={permissions_models.UserTokenVerb.GET}
                ),
            )

        return interface.ConfigurationHookResult(
            environment={"CAPELLACOLLAB_SESSION_API_TOKEN": password},
            config={"session_token_id": token.id},
        )

    def pre_session_termination_hook(
        self,
        request: interface.PreSessionTerminationHookRequest,
    ) -> interface.PreSessionTerminationHookResult:
        token_id = request.session.config.get("session_token_id")
        if not token_id:
            return interface.PreSessionTerminationHookResult()

        if token := tokens_crud.get_token_by_user_and_id(
            request.db, request.session.owner.id, int(token_id)
        ):
            tokens_crud.delete_token(request.db, token)

        return interface.PreSessionTerminationHookResult()
