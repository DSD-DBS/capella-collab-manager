# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import croniter
import pydantic
from sqlalchemy import orm

from capellacollab.core import database


class CreatePlugin(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    username: str | None
    password: str | None
    remote: str


class PatchPlugin(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    username: str | None = None
    password: str | None = None
    remote: str | None = None


class PluginMetadata(pydantic.BaseModel):
    id: str = pydantic.Field(
        title="Plugin identifier",
        description="Unique identifier of the plugin.",
        examples=["hello-world", "test-plugin"],
        min_length=1,
        max_length=50,
    )
    display_name: str | None = pydantic.Field(
        title="Display name of the plugin for the frontend",
        description="Display name for the plugin. The name is used in the frontend to display the plugin. If ommitted, the id is used instead.",
        examples=["Hello world", "A to B synchronization"],
        alias="displayName",
        min_length=0,
        max_length=200,
    )
    description: str | None = pydantic.Field(
        title="Description of the plugin",
        description=(
            "Description of the plugin. "
            "The description should explain the purpose of the plugin. "
            "The user should be able to understand what the plugin does by reading the description."
        ),
        examples=[
            "This plugin runs the hello-world Docker container.",
            "Synchronize the content from A to B.",
        ],
        min_length=0,
        max_length=500,
    )


class PluginTrigger(pydantic.BaseModel):
    cron: str = pydantic.Field(
        title="Cron expression",
        description="If provided and enabled, the pipelines are triggered automatically according to the cron expression.",
        examples=["0 0 * * *", "*/5 * * * *"],
        min_length=0,
        max_length=50,
    )
    manual: bool = pydantic.Field(
        title="Manual trigger",
        description="If true and enabled, the plugin can be triggered manually by the user.",
    )

    @pydantic.field_validator("cron")
    @classmethod
    def validate_cron_expression(cls, value):
        try:
            # Attempt to create a croniter object with the expression
            croniter.croniter(value)
        except (ValueError, croniter.CroniterBadCronError):
            raise ValueError("Invalid cron expression")
        return value


class T4CPluginInputMapping(pydantic.BaseModel):
    host: str = pydantic.Field(
        title="Host of the TeamForCapella server",
        description=(
            "Host of the TeamForCapella server."
            "The host can be a hostname or an IP address,"
            "e.g. `t4c.example.com` or `prod-6-0-0-server-internal.t4c-server.svc.cluster.local`"
        ),
        examples=["T4C_REPO_HOST", "T4C_SERVER_HOST"],
    )
    repository_port: str = pydantic.Field(
        title="Repository port of the TeamForCapella server",
        alias="repositoryPort",
        description=(
            "Repository port of the TeamForCapella server."
            "The default port is 2036."
        ),
        examples=["T4C_REPO_PORT"],
    )
    cdo_port: str = pydantic.Field(
        title="CDO port of the TeamForCapella server",
        alias="cdoPort",
        description=(
            "CDO port of the TeamForCapella server."
            "The default port is 12036."
            "The CDO port is disbabled by default since TeamForCapella version 6.0.0."
        ),
        examples=["T4C_CDO_PORT"],
    )
    repository_name: str = pydantic.Field(
        title="Name of the TeamForCapella repository",
        alias="repositoryName",
        description=(
            "Name of the TeamForCapella repository, "
            "e.g. `repository_without_authentication` or `repoCapella`."
        ),
        examples=["T4C_REPO_NAME", "T4C_REPOSITORY_NAME"],
    )
    project_name: str = pydantic.Field(
        title="Name of the TeamForCapella project",
        alias="projectName",
        description=(
            "Name of the TeamForCapella project, e.g. `test-project`. "
            "Should match the name of the `.project` file in Capella."
        ),
        examples=["T4C_PROJECT_NAME"],
    )
    repository_username: str = pydantic.Field(
        title="Username for the TeamForCapella repository",
        alias="repositoryUsername",
        description=(
            "Username of the TeamForCapella repository user. "
            "A technical user will be auto-generated for the repository."
        ),
        examples=["T4C_USERNAME"],
    )
    repository_password: str = pydantic.Field(
        title="Password for the TeamForCapella repository",
        alias="repositoryPassword",
        description=(
            "Password of the TeamForCapella repository user. "
            "A technical user will be auto-generated for the repository."
        ),
        examples=["T4C_PASSWORD"],
    )


class GitPluginInputMapping(pydantic.BaseModel):
    url: str = pydantic.Field(
        title="HTTP URL of the Git repository",
        description=(
            "HTTP(S) URL of the Git repository, e.g. `https://github.com/DSD-DBS/capella-collab-manager.git`"
        ),
        examples=["GIT_URL", "GIT_REPO_URL"],
    )
    username: str = pydantic.Field(
        title="Username of the Git repository",
        description="Username to authenticate against the Git repository",
        examples=["GIT_USERNAME"],
    )
    password: str = pydantic.Field(
        title="Password of the Git repository",
        description="Password to authenticate against the Git repository",
        examples=["GIT_PASSWORD"],
    )
    revision: str = pydantic.Field(
        title="Revision of the Git repository",
        description="Revision of the Git repository",
        examples=["GIT_REPO_BRANCH", "GIT_REPO_REVISION", "GIT_REVISION"],
    )


class GitPluginInput(pydantic.BaseModel):
    description: str = pydantic.Field(
        title="Description",
        description=(
            "Description of the input. "
            "Will be displayed in the Collaboration Manager frontend before the Git repository selection."
        ),
        examples=[
            "Select the Git repository, which is injected into the pipeline:"
        ],
    )
    type: t.Literal["git"] = pydantic.Field(
        title="Used input type",
        description="Use Git as input type.",
    )
    mapping: GitPluginInputMapping = pydantic.Field(
        title="Mapping of Git repository values from the Capella Collaboration manager database to environment variables.",
        description=(
            "Mapping of Git repository values to environment variables. "
            "The values are mapped to the specificed environment variables. "
            "The pipeline job can read the values from the environment variables."
        ),
    )


class T4CPluginInput(pydantic.BaseModel):
    description: str = pydantic.Field(
        title="Description",
        description=(
            "Description of the input. "
            "Will be displayed in the Collaboration Manager frontend before the TeamForCapella server/repository selection."
        ),
        examples=[
            "Select the TeamForCapella server, which is injected into the pipeline:"
        ],
    )
    type: t.Literal["t4c"] = pydantic.Field(
        title="Used input type",
        description="Use TeamForCapella as input type.",
    )
    mapping: T4CPluginInputMapping = pydantic.Field(
        title="Mapping of TeamForCapella server values from the Capella Collaboration manager database to environment variables.",
        description=(
            "Mapping of TeamForCapella server values to environment variables. "
            "The values are mapped to the specificed environment variables. "
            "The pipeline job can read the values from the environment variables."
        ),
    )


class PluginJob(pydantic.BaseModel):
    image: str = pydantic.Field(
        title="Docker image, including the Docker tag",
        description="Must be a valid Docker image name. It can contain a tag. If no tag is provided, the `:latest` tag is used.",
        examples=["hello-world:latest"],
    )


class PluginContent(pydantic.BaseModel):
    metadata: PluginMetadata = pydantic.Field(
        title="Plugin metadata",
        description="Metadata of the plugin.",
    )
    trigger: PluginTrigger = pydantic.Field(
        title="Plugin trigger",
        description="Defition of trigger rules for the plugin pipelines.",
    )
    input: list[T4CPluginInput | GitPluginInput]
    job: PluginJob = pydantic.Field(
        title="Job definition",
        description="Defition of the plugin job.",
    )


class Plugin(CreatePlugin):
    id: int
    content: PluginContent | None


class DatabasePlugin(database.Base):
    __tablename__ = "plugins"

    id: orm.Mapped[int] = orm.mapped_column(
        unique=True, primary_key=True, index=True
    )
    username: orm.Mapped[str | None]
    password: orm.Mapped[str | None]
    remote: orm.Mapped[str]
    content: orm.Mapped[dict[str, t.Any] | None]
