# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib
import typing as t
from urllib import parse as urllib_parse

from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core import models as core_models
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from .. import models as sessions_models
from . import interface

log = logging.getLogger(__name__)


class JupyterConfigEnvironment(t.TypedDict):
    JUPYTER_BASE_URL: str
    JUPYTER_TOKEN: str
    JUPYTER_PORT: str
    JUPYTER_URI: str
    CSP_ORIGIN_HOST: str


class GeneralConfigEnvironment(t.TypedDict):
    scheme: str
    host: str
    port: str
    wildcardHost: t.NotRequired[bool | None]


class JupyterIntegration(interface.HookRegistration):
    def __init__(self):
        self._jupyter_public_uri: urllib_parse.ParseResult = (
            urllib_parse.urlparse(config["extensions"]["jupyter"]["publicURI"])
        )
        self._general_conf: GeneralConfigEnvironment = config["general"]

    def configuration_hook(  # type: ignore[override]
        self,
        db: orm.Session,
        user: users_models.DatabaseUser,
        tool: tools_models.DatabaseTool,
        **kwargs,
    ) -> tuple[
        JupyterConfigEnvironment,
        list[operators_models.Volume],
        list[core_models.Message],
    ]:
        jupyter_token = credentials.generate_password(length=64)

        environment: JupyterConfigEnvironment = {
            "JUPYTER_TOKEN": jupyter_token,
            "JUPYTER_BASE_URL": self._determine_base_url(user.name),
            "JUPYTER_PORT": "8888",
            "JUPYTER_URI": f'{config["extensions"]["jupyter"]["publicURI"]}/{user.name}/lab?token={jupyter_token}',
            "CSP_ORIGIN_HOST": f"{self._general_conf.get('scheme')}://{self._general_conf.get('host')}:{self._general_conf.get('port')}",
        }

        volumes = self._get_project_share_volume_mounts(db, user.name, tool)

        return environment, volumes, []  # type: ignore[return-value]

    def post_session_creation_hook(
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ):
        assert self._jupyter_public_uri.hostname
        operator.create_public_route(
            session_id=session_id,
            host=self._jupyter_public_uri.hostname or "",
            path=self._determine_base_url(user.name),
            port=8888,
            wildcard_host=self._general_conf.get("wildcardHost", False),
        )

    def pre_session_termination_hook(  # type: ignore
        self,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
        operator.delete_public_route(session_id=session.id)

    def _determine_base_url(self, username: str):
        return f"{self._jupyter_public_uri.path}/{username}"

    def _get_project_share_volume_mounts(
        self,
        db: orm.Session,
        username: str,
        tool: tools_models.DatabaseTool,
    ) -> list[operators_models.PersistentVolume]:
        volumes = []

        accessible_models_with_workspace_configuration = [
            model
            for model in toolmodels_crud.get_models_by_tool(db, tool.id)
            if model.configuration
            and "workspace" in model.configuration
            and self._is_project_member(model, username, db)
        ]

        for model in accessible_models_with_workspace_configuration:
            assert model.configuration
            volumes.append(
                operators_models.PersistentVolume(
                    name=model.configuration["workspace"],
                    read_only=not self._has_project_write_access(
                        model, username, db
                    ),
                    container_path=pathlib.PurePosixPath("/shared")
                    / model.project.slug
                    / model.slug,
                    volume_name="shared-workspace-"
                    + model.configuration["workspace"],
                )
            )

        return volumes

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
