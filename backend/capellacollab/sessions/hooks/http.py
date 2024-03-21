# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

from capellacollab.config import config
from capellacollab.core import models as core_models
from capellacollab.tools import models as tools_models

from .. import models as sessions_models
from .. import util as sessions_util
from . import interface


class GeneralConfigEnvironment(t.TypedDict):
    scheme: str
    host: str
    port: str
    wildcardHost: t.NotRequired[bool | None]


class HTTPIntegration(interface.HookRegistration):
    def __init__(self):
        self._general_conf: GeneralConfigEnvironment = config["general"]

    def session_connection_hook(  # type: ignore[override]
        self,
        db_session: sessions_models.DatabaseSession,
        connection_method: tools_models.ToolSessionConnectionMethod,
        logger: logging.LoggerAdapter,
        **kwargs,
    ) -> interface.SessionConnectionHookResult:
        if not isinstance(
            connection_method, tools_models.HTTPConnectionMethod
        ):
            return interface.SessionConnectionHookResult()

        try:
            redirect_url = connection_method.redirect_url.format(
                **db_session.environment
            )
        except Exception:
            logger.error(
                "Error while formatting the redirect URL", exc_info=True
            )
            return interface.SessionConnectionHookResult(
                warnings=[
                    core_models.Message(
                        title="Couldn't derive the redirect URL.",
                        reason="Please check the backend logs for more information.",
                    )
                ]
            )

        cookies, warnings = sessions_util.resolve_environment_variables(
            logger, db_session.environment, connection_method.cookies
        )

        # Set token for pre-authentication
        cookies |= {
            "ccm_session_token": db_session.environment[
                "CAPELLACOLLAB_SESSION_TOKEN"
            ]
        }

        return interface.SessionConnectionHookResult(
            redirect_url=redirect_url, cookies=cookies, warnings=warnings
        )
