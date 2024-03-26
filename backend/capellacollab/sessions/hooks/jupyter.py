# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import interface

log = logging.getLogger(__name__)


class JupyterIntegration(interface.HookRegistration):
    def configuration_hook(  # type: ignore[override]
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        tool: tools_models.DatabaseTool,
        operator: operators.KubernetesOperator,
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        volumes, warnings = self._get_project_share_volume_mounts(
            db, user.name, tool, operator
        )
        return interface.ConfigurationHookResult(
            volumes=volumes, warnings=warnings
        )

    def _get_project_share_volume_mounts(
        self,
        db: orm.Session,
        username: str,
        tool: tools_models.DatabaseTool,
        operator: operators.KubernetesOperator,
    ) -> tuple[list[operators_models.Volume], list[core_models.Message]]:
        volumes: list[operators_models.Volume] = []
        warnings: list[core_models.Message] = []

        accessible_models_with_workspace_configuration = [
            model
            for model in toolmodels_crud.get_models_by_tool(db, tool.id)
            if model.configuration
            and "workspace" in model.configuration
            and self._is_project_member(model, username, db)
        ]

        for model in accessible_models_with_workspace_configuration:
            assert model.configuration
            volume_name = (
                "shared-workspace-" + model.configuration["workspace"]
            )

            if not operator.persistent_volume_exists(volume_name):
                warnings.append(
                    core_models.Message(
                        err_code="JUPYTER_FILE_SHARE_VOLUME_NOT_FOUND",
                        reason=(
                            f"The Jupyter file-share volume for the model '{model.name}' in the project '{model.project.name}' couldn't be located. "
                            "Please contact your system administrator or recreate the model (this will erase all data in the file-share)."
                        ),
                    )
                )
                continue

            volumes.append(
                operators_models.PersistentVolume(
                    name=model.configuration["workspace"],
                    read_only=not self._has_project_write_access(
                        model, username, db
                    ),
                    container_path=pathlib.PurePosixPath("/shared")
                    / model.project.slug
                    / model.slug,
                    volume_name=volume_name,
                )
            )

        return volumes, warnings

    def _is_project_member(
        self,
        model: toolmodels_models.DatabaseToolModel,
        username: str,
        db: orm.Session,
    ) -> bool:
        return auth_injectables.ProjectRoleVerification(
            required_role=projects_users_models.ProjectUserRole.USER,
            verify=False,
        )(model.project.slug, username, db)

    def _has_project_write_access(
        self,
        model: toolmodels_models.DatabaseToolModel,
        username: str,
        db: orm.Session,
    ) -> bool:
        return auth_injectables.ProjectRoleVerification(
            required_role=projects_users_models.ProjectUserRole.USER,
            required_permission=projects_users_models.ProjectUserPermission.WRITE,
            verify=False,
        )(model.project.slug, username, db)
