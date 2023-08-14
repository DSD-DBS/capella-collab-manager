# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t
from urllib import parse as urllib_parse

from capellacollab.config import config
from capellacollab.core import credentials
from capellacollab.core import models as core_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models
from capellacollab.users import models as users_models

from .. import models as sessions_models
from . import interface

log = logging.getLogger(__name__)


class JupyterConfigEnvironment(t.TypedDict):
    JUPYTER_BASE_URL: str
    JUPYTER_TOKEN: str
    JUPYTER_PORT: str
    CSP_ORIGIN_HOST: str


class JupyterIntegration(interface.HookRegistration):
    def __init__(self):
        self._jupyter_public_uri: urllib_parse.ParseResult = (
            urllib_parse.urlparse(config["extensions"]["jupyter"]["publicURI"])
        )
        self._general_conf = config["general"]

    def configuration_hook(
        self,
        user: users_models.DatabaseUser,
        **kwargs,
    ) -> tuple[
        JupyterConfigEnvironment,
        list[operators_models.Volume],
        list[core_models.Message],
    ]:
        jupyter_token = credentials.generate_password(length=64)

        environment = {
            "JUPYTER_TOKEN": jupyter_token,
            "JUPYTER_BASE_URL": self._determine_base_url(user.name),
            "JUPYTER_PORT": "8888",
            "JUPYTER_URI": f'{config["extensions"]["jupyter"]["publicURI"]}/{user.name}/lab?token={jupyter_token}',
            "CSP_ORIGIN_HOST": f"{self._general_conf.get('scheme')}://{self._general_conf.get('host')}:{self._general_conf.get('port')}",
        }

        return environment, [], []

    def post_session_creation_hook(
        self,
        session_id: str,
        operator: operators.KubernetesOperator,
        user: users_models.DatabaseUser,
        **kwargs,
    ):
        operator.create_public_route(
            session_id=session_id,
            host=self._jupyter_public_uri.hostname,
            path=self._determine_base_url(user.name),
            port=8888,
        )

    def pre_session_termination_hook(
        self,
        operator: operators.KubernetesOperator,
        session: sessions_models.DatabaseSession,
        **kwargs,
    ):
        operator.delete_public_route(session_id=session.id)

    def _determine_base_url(self, username: str):
        return f"{self._jupyter_public_uri.path}/{username}"
