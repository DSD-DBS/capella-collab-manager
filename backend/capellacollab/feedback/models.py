# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum
import typing as t

import pydantic

from capellacollab.core import models as core_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.sessions.models import SessionType
from capellacollab.tools import models as tools_models


class FeedbackRating(str, enum.Enum):
    GOOD = "good"
    OKAY = "okay"
    BAD = "bad"


class AnonymizedSession(core_pydantic.BaseModel):
    id: str
    type: SessionType
    created_at: datetime.datetime

    version: tools_models.ToolVersionWithTool

    state: str = pydantic.Field(default="UNKNOWN")
    warnings: list[core_models.Message] = pydantic.Field(default=[])

    connection_method_id: str
    connection_method: tools_models.ToolSessionConnectionMethod | None = None


class Feedback(core_pydantic.BaseModel):
    rating: FeedbackRating = pydantic.Field(
        description="The rating of the feedback"
    )
    feedback_text: t.Optional[str] = pydantic.Field(
        description="The feedback text"
    )
    share_contact: bool = pydantic.Field(
        description="Whether the user wants to share their contact information"
    )
    sessions: list[AnonymizedSession] = pydantic.Field(
        description="The sessions the feedback is for"
    )
    trigger: str = pydantic.Field(
        description="What triggered the feedback form"
    )
