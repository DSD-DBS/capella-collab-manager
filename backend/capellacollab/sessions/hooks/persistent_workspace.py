# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.users import models as users_models

from . import interface


class PersistentWorkspacEnvironment(t.TypedDict):
    pass


class PersistentWorkspaceHook(interface.HookRegistration):
    """Takes care of the persistent workspace of a user.

    Is responsible for mounting the persistent workspace into persistent sessions.
    """

    def configuration_hook(  # type: ignore
        self,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        session_type: sessions_models.SessionType,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type == sessions_models.SessionType.READONLY:
            # Skip read-only sessions, no persistent workspace needed.
            return interface.ConfigurationHookResult()

        volume_name = self._create_persistent_workspace(operator, user.name)
        volume = operators_models.PersistentVolume(
            name="workspace",
            read_only=False,
            container_path=pathlib.PurePosixPath("/workspace"),
            volume_name=volume_name,
        )

        return interface.ConfigurationHookResult(
            volumes=[volume],
        )

    def _get_volume_name(self, username: str) -> str:
        return "persistent-session-" + self._normalize_username(username)

    def _normalize_username(self, username: str) -> str:
        return username.replace("@", "-at-").replace(".", "-dot-").lower()

    def _create_persistent_workspace(
        self, operator: operators.KubernetesOperator, username: str
    ) -> str:
        persistent_workspace_name = self._get_volume_name(username)
        operator.create_persistent_volume(
            persistent_workspace_name,
            "20Gi",
            labels={
                "capellacollab/username": self._normalize_username(username),
            },
        )
        return persistent_workspace_name
