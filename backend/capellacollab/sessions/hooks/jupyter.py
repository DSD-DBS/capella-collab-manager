# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from . import interface

log = logging.getLogger(__name__)


class JupyterIntegration(interface.HookRegistration):
    def configuration_hook(
        self,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        volumes, warnings = self._get_project_share_volume_mounts(
            request.db,
            request.tool,
            request.operator,
            request.user,
            request.pat,
            request.global_scope,
        )
        return interface.ConfigurationHookResult(
            volumes=volumes, warnings=warnings
        )

    def _get_project_share_volume_mounts(
        self,
        db: orm.Session,
        tool: tools_models.DatabaseTool,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        pat: tokens_models.DatabaseUserToken | None,
        global_scope: permissions_models.GlobalScopes,
    ) -> tuple[list[operators_models.Volume], list[core_models.Message]]:
        volumes: list[operators_models.Volume] = []
        warnings: list[core_models.Message] = []

        accessible_models_with_workspace_configuration = [
            model
            for model in toolmodels_crud.get_models_by_tool(db, tool.id)
            if model.configuration
            and "workspace" in model.configuration
            and self._has_access_to_volume_share(
                model.project,
                db,
                user,
                pat,
                global_scope,
                permissions_models.UserTokenVerb.GET,
            )
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
                        title="Jupyter file-share volume not found",
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
                    read_only=not self._has_access_to_volume_share(
                        model.project,
                        db,
                        user,
                        pat,
                        global_scope,
                        permissions_models.UserTokenVerb.UPDATE,
                    ),
                    container_path=pathlib.PurePosixPath("/shared")
                    / model.project.slug
                    / model.slug,
                    volume_name=volume_name,
                    sub_path=None,
                )
            )

        return volumes, warnings

    def _has_access_to_volume_share(
        self,
        project: projects_models.DatabaseProject,
        db: orm.Session,
        user: users_models.DatabaseUser,
        pat: tokens_models.DatabaseUserToken | None,
        global_scope: permissions_models.GlobalScopes,
        required_verb: permissions_models.UserTokenVerb,
    ) -> bool:
        project_scope = projects_permissions_injectables.get_scope(
            (user, pat), global_scope, project, db
        )
        return required_verb in project_scope.shared_volumes
