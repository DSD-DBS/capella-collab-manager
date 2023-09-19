# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import typing as t

import requests
from sqlalchemy import orm

from capellacollab.core import credentials
from capellacollab.core import models as core_models
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.sessions.operators import models as operators_models
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as repo_crud,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    interface as repo_interface,
)
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as sessions_models
from . import interface

log = logging.getLogger(__name__)


class T4CConfigEnvironment(t.TypedDict):
    T4C_LICENCE_SECRET: str
    T4C_JSON: str
    T4C_USERNAME: str
    T4C_PASSWORD: str


class T4CIntegration(interface.HookRegistration):
    def configuration_hook(  # type: ignore
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        tool_version: tools_models.DatabaseVersion,
        token: dict[str, t.Any],
        **kwargs,
    ) -> tuple[
        T4CConfigEnvironment,
        list[operators_models.Volume],
        list[core_models.Message],
    ]:
        warnings: list[core_models.Message] = []

        # When using a different tool with TeamForCapella support (e.g., Capella + pure::variants),
        # the version ID doesn't match the version from the T4C integration.
        # We have to find the matching Capella version by name.
        t4c_repositories = repo_crud.get_user_t4c_repositories(
            db, tool_version.name, user
        )

        t4c_json = json.dumps(
            [
                {
                    "repository": repository.name,
                    "protocol": repository.instance.protocol,
                    "port": repository.instance.http_port
                    if repository.instance.protocol == "ws"
                    else repository.instance.port,
                    "host": repository.instance.host,
                    "instance": repository.instance.name,
                }
                for repository in t4c_repositories
            ]
        )

        t4c_licence_secret = (
            t4c_repositories[0].instance.license if t4c_repositories else ""
        )

        environment = T4CConfigEnvironment(
            T4C_LICENCE_SECRET=t4c_licence_secret,
            T4C_JSON=t4c_json,
            T4C_USERNAME=user.name,
            T4C_PASSWORD=credentials.generate_password(),
        )

        for repository in t4c_repositories:
            try:
                repo_interface.add_user_to_repository(
                    repository.instance,
                    repository.name,
                    username=user.name,
                    password=environment["T4C_PASSWORD"],
                    is_admin=auth_injectables.RoleVerification(
                        required_role=users_models.Role.ADMIN, verify=False
                    )(token, db),
                )
            except requests.RequestException:
                warnings.append(
                    core_models.Message(
                        reason=(
                            f"The creation of your user in the repository '{repository.name}' of the the instance '{repository.instance.name}' failed.",
                            "Most likely this is due to a downtime of the corresponding TeamForCapella server.",
                            "If you don't need access to the repository you can still use the session.",
                        )
                    )
                )
                log.warning(
                    "Could not add user to t4c repository '%s' of instance '%s'",
                    repository.name,
                    repository.instance.name,
                    exc_info=True,
                )

        return environment, [], warnings

    def pre_session_termination_hook(  # type: ignore
        self,
        db: orm.Session,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
        if session.type == sessions_models.WorkspaceType.PERSISTENT:
            self._revoke_session_tokens(db, session)

    def _revoke_session_tokens(
        self,
        db: orm.Session,
        session: sessions_models.DatabaseSession,
    ):
        for repository in repo_crud.get_user_t4c_repositories(
            db, session.version.name, session.owner
        ):
            try:
                repo_interface.remove_user_from_repository(
                    repository.instance, repository.name, session.owner.name
                )
            except requests.RequestException:
                log.exception(
                    "Could not delete user '%s' from repository '%s' of instance '%s'. Please delete the user manually.",
                    session.owner.name,
                    repository.name,
                    repository.instance.name,
                    exc_info=True,
                )
