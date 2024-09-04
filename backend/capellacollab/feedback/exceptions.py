# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class SmtpNotSetupError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="SMTP is not set up",
            reason="SMTP must be set up to perform this action",
            err_code="SMTP_NOT_SETUP",
        )


class FeedbackNotEnabledError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Feedback is not set enabled",
            reason="Feedback must be set up to perform this action",
            err_code="FEEDBACK_NOT_SETUP",
        )
