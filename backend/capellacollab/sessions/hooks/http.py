# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from capellacollab.core import models as core_models
from capellacollab.tools import models as tools_models

from .. import models as sessions_models
from .. import util as sessions_util
from . import interface


class HTTPIntegration(interface.HookRegistration):
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
                        err_code="REDIRECT_URL_DERIVATION_FAILED",
                        title="Couldn't derive the redirect URL",
                        reason="Please check the backend logs for more information.",
                    )
                ]
            )

        cookies, warnings = sessions_util.resolve_environment_variables(
            logger, db_session.environment, connection_method.cookies
        )

        return interface.SessionConnectionHookResult(
            redirect_url=redirect_url, cookies=cookies, warnings=warnings
        )
