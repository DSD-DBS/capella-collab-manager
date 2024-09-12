# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class TooManyOutStandingRequests(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            title="Too many outstanding requests",
            reason="Too many outstanding requests. Please try again later.",
            err_code="LOKI_TOO_MANY_OUTSTANDING_REQUESTS",
        )


class GrafanaLokiDisabled(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Grafana Loki is disabled for this instance.",
            reason="To use this feature, ask your system administrator to enable Grafana Loki.",
            err_code="LOKI_DISABLED",
        )
