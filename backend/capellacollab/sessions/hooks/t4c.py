# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import typing as t

import requests
from sqlalchemy import orm

from capellacollab.core import credentials
from capellacollab.core import models as core_models
from capellacollab.permissions import models as permissions_models
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    crud as repo_crud,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    interface as repo_interface,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    models as repo_models,
)

from .. import models as sessions_models
from . import interface


class T4CConfigEnvironment(t.TypedDict):
    T4C_LICENCE_SECRET: str
    T4C_JSON: str
    T4C_USERNAME: str
    T4C_PASSWORD: str


class T4CIntegration(interface.HookRegistration):
    def configuration_hook(
        self, request: interface.ConfigurationHookRequest
    ) -> interface.ConfigurationHookResult:
        user = request.user

        if request.session_type != sessions_models.SessionType.PERSISTENT:
            # Skip non-persistent sessions, no T4C integration needed.
            return interface.ConfigurationHookResult()

        warnings: list[core_models.Message] = []

        t4c_repositories = repo_crud.get_user_t4c_repositories(
            request.db, request.tool_version, user, request.global_scope
        )

        t4c_json = json.dumps(
            [
                {
                    "repository": repository.name,
                    "protocol": repository.instance.protocol,
                    "port": (
                        repository.instance.http_port
                        if repository.instance.protocol == "ws"
                        else repository.instance.port
                    ),
                    "host": repository.instance.host,
                    "instance": repository.instance.name,
                }
                for repository in t4c_repositories
            ]
        )

        config = {
            "t4c_repositories": json.dumps(
                [repository.id for repository in t4c_repositories]
            )
        }

        t4c_licence_secret = (
            t4c_repositories[0].instance.license_server.license_key
            if t4c_repositories
            else ""
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
                    is_admin=permissions_models.UserTokenVerb.UPDATE
                    in request.global_scope.admin.t4c_repositories,
                )
            except requests.RequestException:
                warnings.append(
                    core_models.Message(
                        err_code="T4C_USER_CREATION_FAILED",
                        title="Could not create user in TeamForCapella repository",
                        reason=(
                            f"The creation of your user in the repository '{repository.name}' of the the instance '{repository.instance.name}' failed. "
                            "Most likely this is due to a downtime of the corresponding TeamForCapella server. "
                            "If you don't need access to the repository you can still use the session."
                        ),
                    )
                )
                request.logger.warning(
                    "Could not add user to t4c repository '%s' of instance '%s'",
                    repository.name,
                    repository.instance.name,
                    exc_info=True,
                )

        return interface.ConfigurationHookResult(
            environment=environment, warnings=warnings, config=config
        )

    def pre_session_termination_hook(
        self, request: interface.PreSessionTerminationHookRequest
    ):
        if request.session.type == sessions_models.SessionType.PERSISTENT:
            if "t4c_repositories" in request.session.config:
                self._revoke_session_tokens(
                    request.session.config["t4c_repositories"],
                    request.db,
                    request.session,
                    request.logger,
                )
            else:
                # Session was created before t4c_repositories config was introduced
                self._revoke_session_tokens_legacy(
                    request.db,
                    request.session,
                    request.global_scope,
                    request.logger,
                )

    def session_connection_hook(
        self,
        request: interface.SessionConnectionHookRequest,
    ) -> interface.SessionConnectionHookResult:
        if request.db_session.type != sessions_models.SessionType.PERSISTENT:
            return interface.SessionConnectionHookResult()

        if request.db_session.owner != request.user:
            # The session is shared, don't provide the T4C token.
            return interface.SessionConnectionHookResult()

        return interface.SessionConnectionHookResult(
            t4c_token=request.db_session.environment.get("T4C_PASSWORD")
        )

    @classmethod
    def _revoke_session_tokens(
        cls,
        t4c_config: str,
        db: orm.Session,
        session: sessions_models.DatabaseSession,
        logger: logging.LoggerAdapter,
    ):
        """Remove session tokens using configuration"""
        for repository_id in json.loads(t4c_config):
            repository = repo_crud.get_t4c_repository_by_id(db, repository_id)
            if not repository:
                logger.error(
                    "Could not delete user '%s' from repository '%d'. The repository doesn't exist. Please delete the user manually.",
                    session.owner.name,
                    repository_id,
                )
                continue

            cls._remove_user_from_repository(
                repository, session.owner.name, logger
            )

    @classmethod
    def _revoke_session_tokens_legacy(
        cls,
        db: orm.Session,
        session: sessions_models.DatabaseSession,
        global_scope: permissions_models.GlobalScopes,
        logger: logging.LoggerAdapter,
    ):
        """Remove session tokens using access evaluation"""
        for repository in repo_crud.get_user_t4c_repositories(
            db, session.version, session.owner, global_scope
        ):
            cls._remove_user_from_repository(
                repository, session.owner.name, logger
            )

    @classmethod
    def _remove_user_from_repository(
        cls,
        repository: repo_models.DatabaseT4CRepository,
        username: str,
        logger: logging.LoggerAdapter,
    ):
        try:
            repo_interface.remove_user_from_repository(
                repository.instance, repository.name, username
            )
        except requests.RequestException:
            logger.exception(
                "Could not delete user '%s' from repository '%s' of instance '%s'. Please delete the user manually.",
                username,
                repository.name,
                repository.instance.name,
            )
