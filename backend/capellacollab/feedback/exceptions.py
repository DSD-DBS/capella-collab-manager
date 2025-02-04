# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class FeedbackNotEnabledError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Feedback is not enabled",
            reason="Feedback must be set up to perform this action",
            err_code="FEEDBACK_NOT_ENABLED",
        )

    @classmethod
    def openapi_example(cls) -> "FeedbackNotEnabledError":
        return cls()


class NoFeedbackRecipientsError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="The list of recipients is empty",
            reason="Feedback can only be activated when there are recipients.",
            err_code="FEEDBACK_MISSING_RECIPIENTS",
        )

    @classmethod
    def openapi_example(cls) -> "NoFeedbackRecipientsError":
        return cls()
