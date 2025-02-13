# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core import models as core_models
from capellacollab.tools import models as tools_models

from .. import util as sessions_util
from . import interface


class HTTPIntegration(interface.HookRegistration):
    def session_connection_hook(
        self, request: interface.SessionConnectionHookRequest
    ) -> interface.SessionConnectionHookResult:
        if not isinstance(
            request.connection_method, tools_models.HTTPConnectionMethod
        ):
            return interface.SessionConnectionHookResult()

        try:
            redirect_url = request.connection_method.redirect_url.format(
                **request.db_session.environment
            )
        except Exception:
            request.logger.exception(
                "Error while formatting the redirect URL"
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
            request.logger,
            request.db_session.environment,
            request.connection_method.cookies,
        )

        return interface.SessionConnectionHookResult(
            redirect_url=redirect_url, cookies=cookies, warnings=warnings
        )
