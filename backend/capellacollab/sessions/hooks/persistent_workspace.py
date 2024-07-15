# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t
import uuid

from sqlalchemy import orm

from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models
from capellacollab.users.workspaces import crud as users_workspaces_crud
from capellacollab.users.workspaces import models as users_workspaces_models

from . import interface


class PersistentWorkspacEnvironment(t.TypedDict):
    pass


class PersistentWorkspaceHook(interface.HookRegistration):
    """Takes care of the persistent workspace of a user.

    Is responsible for mounting the persistent workspace into persistent sessions.
    """

    def configuration_hook(  # type: ignore
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        session_type: sessions_models.SessionType,
        tool: tools_models.DatabaseTool,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        if session_type == sessions_models.SessionType.READONLY:
            # Skip read-only sessions, no persistent workspace needed.
            return interface.ConfigurationHookResult()

        self._check_that_persistent_workspace_is_allowed(tool)

        volume_name = self._create_persistent_workspace(db, operator, user)
        volume = operators_models.PersistentVolume(
            name="workspace",
            read_only=False,
            container_path=pathlib.PurePosixPath("/workspace"),
            volume_name=volume_name,
        )

        return interface.ConfigurationHookResult(
            volumes=[volume],
        )

    def _check_that_persistent_workspace_is_allowed(
        self, tool: tools_models.DatabaseTool
    ):
        if not tool.config.persistent_workspaces.mounting_enabled:
            raise sessions_exceptions.WorkspaceMountingNotAllowedError(
                tool.name
            )

    def _create_persistent_workspace(
        self,
        db: orm.Session,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
    ) -> str:
        workspaces = users_workspaces_crud.get_workspaces_for_user(db, user)
        persistent_workspace_name = "workspace-" + str(uuid.uuid4())
        size = "20Gi"

        if len(workspaces) > 0:
            persistent_workspace_name = workspaces[0].pvc_name
        else:
            users_workspaces_crud.create_workspace(
                db,
                workspace=users_workspaces_models.DatabaseWorkspace(
                    pvc_name=persistent_workspace_name,
                    size=size,
                    user=user,
                ),
            )

        operator.create_persistent_volume(
            persistent_workspace_name,
            size,
            annotations={
                "capellacollab/username": user.name,
                "capellacollab/user-id": str(user.id),
                "capellacollab/volume": "personal-workspace",
            },
        )

        return persistent_workspace_name
