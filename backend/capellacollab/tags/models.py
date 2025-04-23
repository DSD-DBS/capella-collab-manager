# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import re
import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject


class CreateTag(core_pydantic.BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    hex_color: str = pydantic.Field(examples=["#FF5733"])

    @pydantic.field_validator("hex_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", value):
            raise ValueError(f"{value} is not a valid HEX color code")
        return value


class Tag(CreateTag):
    id: int


class DatabaseTag(database.Base):
    __tablename__ = "tags"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, unique=True, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    description: orm.Mapped[str | None] = orm.mapped_column(default=None)
    icon: orm.Mapped[str | None] = orm.mapped_column(default=None)
    hex_color: orm.Mapped[str] = orm.mapped_column(default=None)

    projects: orm.Mapped[list["DatabaseProject"]] = orm.relationship(
        "DatabaseProject",
        secondary="projects_tags_association",
        back_populates="tags",
        default_factory=list,
    )
