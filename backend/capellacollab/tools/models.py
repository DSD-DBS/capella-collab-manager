# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.database import decorator

DOCKER_IMAGE_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_\-/.:${}]*$"


class ToolIntegrations(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    t4c: bool = pydantic.Field(
        default=False,
        description=(
            "Enables support for TeamForCapella. "
            "If enabled, TeamForCapella repositories will be shown as model sources for corresponding models. "
            "Also, session tokens are created for corresponding sessions. "
            "Please refer to the documentation for more details. "
        ),
    )
    pure_variants: bool = pydantic.Field(
        default=False,
        description=(
            "Enables support for pure::variants. "
            "If enabled and the restrictions are met, pure::variants license secrets & information will be mounted to containers. "
            "Please refer to the documentation for more details. "
        ),
    )
    jupyter: bool = pydantic.Field(
        default=False,
        description="Activate if the used tool is Jupyter. ",
    )


class DatabaseTool(database.Base):
    __tablename__ = "tools"

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)

    name: orm.Mapped[str]

    integrations: orm.Mapped[ToolIntegrations] = orm.mapped_column(
        decorator.PydanticDecorator(ToolIntegrations), nullable=False
    )

    versions: orm.Mapped[list[DatabaseVersion]] = orm.relationship(
        default_factory=list, back_populates="tool"
    )
    natures: orm.Mapped[list[DatabaseNature]] = orm.relationship(
        default_factory=list, back_populates="tool"
    )


class ReadOnlySessionToolConfiguration(pydantic.BaseModel):
    image: str | None = pydantic.Field(
        default="docker.io/hello-world:latest",
        pattern=DOCKER_IMAGE_PATTERN,
        examples=[
            "docker.io/hello-world:latest",
            "ghcr.io/dsd-dbs/capella-dockerimages/capella/readonly:{version}-main",
        ],
        description=(
            "Docker image, which is used for read-only sessions. "
            "If set to None, read-only session support will be disabled for this tool version. "
            "You can use '{version}' in the image, which will be replaced with the version name of the tool. "
            "Always use tags to prevent breaking updates. "
        ),
    )


class PersistentSessionToolConfiguration(pydantic.BaseModel):
    image: str | None = pydantic.Field(
        default="docker.io/hello-world:latest",
        pattern=DOCKER_IMAGE_PATTERN,
        examples=[
            "docker.io/hello-world:latest",
            "ghcr.io/dsd-dbs/capella-dockerimages/capella/remote:{version}-main",
        ],
        description=(
            "Docker image, which is used for persistent sessions. "
            "If set to None, persistent session support will be disabled for this tool version. "
            "You can use '{version}' in the image, which will be replaced with the version name of the tool. "
            "Always use tags to prevent breaking updates. "
        ),
    )


class ToolBackupConfiguration(pydantic.BaseModel):
    image: str | None = pydantic.Field(
        default="docker.io/hello-world:latest",
        pattern=DOCKER_IMAGE_PATTERN,
        examples=[
            "docker.io/hello-world:latest",
            "ghcr.io/dsd-dbs/capella-dockerimages/capella/base:{version}-main",
        ],
        description=(
            "Docker image, which is used for backup pipelines. "
            "If set to None, it will no longer be possible to create or spawn a backup pipelines for this tool version. "
            "You can use '{version}' in the image, which will be replaced with the version name of the tool. "
            "Always use tags to prevent breaking updates. "
        ),
    )


class SessionToolConfiguration(pydantic.BaseModel):
    persistent: PersistentSessionToolConfiguration = pydantic.Field(
        default=PersistentSessionToolConfiguration()
    )
    read_only: ReadOnlySessionToolConfiguration = pydantic.Field(
        default=ReadOnlySessionToolConfiguration()
    )


class ToolVersionConfiguration(pydantic.BaseModel):
    is_recommended: bool = pydantic.Field(
        default=False,
        description="Version will be displayed as recommended.",
    )
    is_deprecated: bool = pydantic.Field(
        default=False,
        description="Version will be displayed as deprecated.",
    )

    sessions: SessionToolConfiguration = pydantic.Field(
        default=SessionToolConfiguration(),
        description="Configuration for sessions.",
    )

    backups: ToolBackupConfiguration = pydantic.Field(
        default=ToolBackupConfiguration(),
        description="Configuration for the backup pipelines.",
    )


class DatabaseVersion(database.Base):
    __tablename__ = "versions"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)

    name: orm.Mapped[str]

    config: orm.Mapped[ToolVersionConfiguration] = orm.mapped_column(
        decorator.PydanticDecorator(ToolVersionConfiguration)
    )

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id"),
        init=False,
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(
        back_populates="versions"
    )


class DatabaseNature(database.Base):
    __tablename__ = "types"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)
    name: orm.Mapped[str]

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id"), init=False
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(back_populates="natures")


class CreateTool(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    name: str = pydantic.Field(default="", min_length=2, max_length=30)
    integrations: ToolIntegrations = pydantic.Field(default=ToolIntegrations())


class ToolBase(CreateTool, decorator.PydanticDatabaseModel):
    pass


class ToolConfiguration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    name: str

    versions: list[ToolVersionBase]
    natures: list[ToolNatureBase]

    integrations: ToolIntegrations

    sessions: None
    backups: None


class CreateToolNature(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    name: str = pydantic.Field(default="", min_length=2, max_length=30)


class CreateToolVersion(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    name: str = pydantic.Field(default="", min_length=2, max_length=30)

    config: ToolVersionConfiguration = pydantic.Field(
        default=ToolVersionConfiguration()
    )


class ToolVersionBase(CreateToolVersion, decorator.PydanticDatabaseModel):
    pass


class ToolVersionWithTool(ToolVersionBase):
    tool: ToolBase


class ToolNatureBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
