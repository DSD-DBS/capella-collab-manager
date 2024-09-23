# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import pydantic

from capellacollab.core import models as core_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models


class FeedbackRating(str, enum.Enum):
    BAD = "bad"
    OKAY = "okay"
    GOOD = "good"


class AnonymizedSession(core_pydantic.BaseModel):
    id: str
    type: sessions_models.SessionType
    created_at: datetime.datetime

    version: tools_models.MinimalToolVersionWithTool

    state: str = pydantic.Field(default="UNKNOWN")
    warnings: list[core_models.Message] = pydantic.Field(default=[])

    connection_method: (
        tools_models.MinimalToolSessionConnectionMethod | None
    ) = None


class Feedback(core_pydantic.BaseModel):
    rating: FeedbackRating = pydantic.Field(
        description="The rating of the feedback"
    )
    feedback_text: str | None = pydantic.Field(
        description="The feedback text", max_length=255
    )
    share_contact: bool = pydantic.Field(
        description="Whether the user wants to share their contact information"
    )
    sessions: list[AnonymizedSession] = pydantic.Field(
        description="The sessions the feedback is for"
    )
    trigger: str | None = pydantic.Field(
        description="What triggered the feedback form", max_length=255
    )
