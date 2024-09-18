# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class SMTPNotConfiguredError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="SMTP is not configured",
            reason="SMTP must be configured in the application configuration before sending emails and activating related features.",
            err_code="SMTP_NOT_CONFIGURED",
        )
