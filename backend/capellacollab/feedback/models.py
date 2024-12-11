# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import models as core_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


class FeedbackRating(str, enum.Enum):
    BAD = "bad"
    OKAY = "okay"
    GOOD = "good"


class DatabaseFeedback(database.Base):
    __tablename__ = "feedback"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )
    rating: orm.Mapped[FeedbackRating]
    feedback_text: orm.Mapped[str | None]

    user_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("users.id"),
        init=False,
    )
    user: orm.Mapped[users_models.DatabaseUser | None] = orm.relationship(
        foreign_keys=[user_id],
        cascade="all, delete-orphan",
        single_parent=True,
    )
    beta_tester: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        nullable=False,
        server_default="false",
    )

    trigger: orm.Mapped[str | None]
    created_at: orm.Mapped[datetime.datetime]


class AnonymizedSession(core_pydantic.BaseModel):
    id: str
    type: sessions_models.SessionType
    created_at: datetime.datetime

    version: tools_models.MinimalToolVersionWithTool

    preparation_state: sessions_models.SessionPreparationState = (
        pydantic.Field(default=sessions_models.SessionPreparationState.UNKNOWN)
    )
    state: sessions_models.SessionState = pydantic.Field(
        default=sessions_models.SessionState.UNKNOWN
    )
    warnings: list[core_models.Message] = pydantic.Field(default=[])

    connection_method: (
        tools_models.MinimalToolSessionConnectionMethod | None
    ) = None


class Feedback(core_pydantic.BaseModel):
    rating: FeedbackRating = pydantic.Field(
        description="The rating of the feedback"
    )
    feedback_text: str | None = pydantic.Field(
        description="The feedback text", max_length=500
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
