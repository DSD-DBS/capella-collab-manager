# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t
import uuid

import lxml.etree
import pydantic
import sqlalchemy as sa
from lxml.html import builder
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.database import decorator

DOCKER_IMAGE_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_\-/.:${}]*$"


class SessionPorts(pydantic.BaseModel):
    metrics: int = pydantic.Field(
        default=9118,
        description="Port of the metrics endpoint in the container.",
    )


class RDPPorts(SessionPorts):
    rdp: int = pydantic.Field(
        default=3389, description="Port of the RDP server in the container."
    )


class HTTPPorts(SessionPorts):
    http: int = pydantic.Field(
        default=8080, description="Port of the HTTP server in the container."
    )


def uuid_factory() -> str:
    return str(uuid.uuid4())


class ToolSessionEnvironmentStage(str, enum.Enum):
    BEFORE = "before"
    AFTER = "after"


class ToolSessionEnvironment(pydantic.BaseModel):
    stage: ToolSessionEnvironmentStage = pydantic.Field(
        default=ToolSessionEnvironmentStage.AFTER,
        description=(
            "Stage of the environment variable injection. "
            "'before' runs before the environment variable is stringified, allowing extended filtering and manipulation. "
            "For example, you can access the path of the first provisioned model with '{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}'. "
            "If you provide a dict, it will use Pythons default dict serialization and will not JSON serialization! "
            "'after' runs after the environment variable is JSON serialized, allowing to access a dict in the JSON format. "
        ),
    )
    value: str = pydantic.Field(
        default={"RMT_PASSWORD": "{CAPELLACOLLAB_SESSION_TOKEN}"},
        description=(
            "Environment variables, which are mounted into session containers. "
            "You can use f-strings to reference other environment variables in the value. "
        ),
        examples=[
            {
                "MY_TOOL_USERNAME_WITH_PREFIX": "test_{CAPELLACOLLAB_SESSION_REQUESTER_USERNAME}",
            }
        ],
    )


class ToolSessionConnectionMethod(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=uuid_factory)
    type: str
    name: str = pydantic.Field(default="default")
    description: str = pydantic.Field(default="")
    ports: SessionPorts
    environment: dict[str, str | ToolSessionEnvironment] = pydantic.Field(
        default={},
        description=(
            "Connection method specific environment variables. "
            "Check the global environment field for more information. "
        ),
    )


class GuacamoleConnectionMethod(ToolSessionConnectionMethod):
    type: t.Literal["guacamole"] = "guacamole"
    ports: RDPPorts = pydantic.Field(default=RDPPorts())


class HTTPConnectionMethod(ToolSessionConnectionMethod):
    type: t.Literal["http"] = "http"
    redirect_url: str = pydantic.Field(default="http://localhost:8080")
    ports: HTTPPorts = pydantic.Field(default=HTTPPorts())
    cookies: dict[str, str] = pydantic.Field(
        default={},
        description=(
            "Cookies, which are required to connect to the session. "
        ),
    )


class ToolSessionConnection(pydantic.BaseModel):
    methods: list[GuacamoleConnectionMethod | HTTPConnectionMethod] = (
        pydantic.Field(
            default=[GuacamoleConnectionMethod(), HTTPConnectionMethod()],
            min_length=1,
            max_length=10,
        )
    )

    @pydantic.field_validator("methods")
    @classmethod
    def check_uniqueness_of_method_identifier(
        cls, value: list[HTTPConnectionMethod]
    ) -> list[HTTPConnectionMethod]:
        ids = [method.id for method in value]
        if len(ids) != len(set(ids)):
            raise ValueError(
                "Identifiers of connection methods must be unique."
            )
        return value


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


RESOURCES_DOCS = (
    "To find the right value, you can use the Kubernetes dashboard to monitor the resource usage of the tool. "
    "Refer to the Kubernetes documentation for more details: "
    "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits"
)


class CPUResources(pydantic.BaseModel):
    requests: float = pydantic.Field(
        default=0.4,
        description=(
            "Each session gets at least the specified amount of physical or virtual CPU cores. "
            "An inaccurate value can lead to higher costs. " + RESOURCES_DOCS
        ),
        le=4,
        gt=0,
        examples=[0.5, 2],
    )
    limits: float = pydantic.Field(
        default=2,
        description=(
            "Each session can not consume more than the specified amount of physical or virtual CPU cores. "
            "A high value can lead to high costs, while a low value can lead to performance issues. "
            + RESOURCES_DOCS
        ),
        le=8,
        gt=0,
        examples=[0.8, 3],
    )


class MemoryResources(pydantic.BaseModel):
    requests: str = pydantic.Field(
        default="1.6Gi",
        description=(
            "Each session gets at least the specified amount of memory. "
            "An inaccurate value can lead to higher costs. " + RESOURCES_DOCS
        ),
        examples=["100Mi", "1.6Gi", "2Gi"],
    )
    limits: str = pydantic.Field(
        default="6Gi",
        description=(
            "Each session is limited to the specified amount of memory. "
            "If the session exceeds the limit, it will be terminated and recreated automatically. "
            "A high value can lead to high costs, while a low value can lead unwanted session termination and potential data loss. "
            + RESOURCES_DOCS
        ),
        examples=["200Mi", "6Gi", "10Gi"],
    )


class Resources(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    cpu: CPUResources = pydantic.Field(
        default=CPUResources(),
        description="Configuration about the number of CPU cores that sessions can use.",
    )
    memory: MemoryResources = pydantic.Field(
        default=MemoryResources(),
        description="Configuration about the amount of memory that sessions can use.",
    )


class PrometheusConfiguration(pydantic.BaseModel):
    path: str = pydantic.Field(default="/prometheus")


class SessionMonitoring(pydantic.BaseModel):
    prometheus: PrometheusConfiguration = pydantic.Field(
        default=PrometheusConfiguration(),
        description="Configuration for monitoring and garbage collection.",
    )


class ToolModelProvisioning(pydantic.BaseModel):
    directory: str = pydantic.Field(
        default="/models",
        description=(
            "Directory, where models are provisioned. "
            "The directory is mounted into the session container."
        ),
        examples=["/models", "/provisioned"],
    )
    max_number_of_models: int | None = pydantic.Field(
        default=None,
        description=(
            "Maximum number of models that can be provisioned. "
            "If set to None, there is no limit."
        ),
        examples=[None, 1],
    )


class ToolSessionConfiguration(pydantic.BaseModel):
    resources: Resources = pydantic.Field(default=Resources())
    environment: dict[str, str | ToolSessionEnvironment] = pydantic.Field(
        default={"RMT_PASSWORD": "{CAPELLACOLLAB_SESSION_TOKEN}"},
        description=(
            "Environment variables, which are mounted into session containers. "
            "You can use f-strings to reference other environment variables in the value. "
        ),
        examples=[
            {
                "MY_TOOL_USERNAME_WITH_PREFIX": "test_{CAPELLACOLLAB_SESSION_REQUESTER_USERNAME}",
            }
        ],
    )
    connection: ToolSessionConnection = pydantic.Field(
        default=ToolSessionConnection()
    )
    monitoring: SessionMonitoring = pydantic.Field(default=SessionMonitoring())
    provisioning: ToolModelProvisioning = pydantic.Field(
        default=ToolModelProvisioning(),
        description="Configuration regarding read-only sessions & automatic session provisioning.",
    )


class DatabaseTool(database.Base):
    __tablename__ = "tools"

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)

    name: orm.Mapped[str]

    integrations: orm.Mapped[ToolIntegrations] = orm.mapped_column(
        decorator.PydanticDecorator(ToolIntegrations),
        nullable=False,
        default_factory=ToolIntegrations,
    )

    config: orm.Mapped[ToolSessionConfiguration] = orm.mapped_column(
        decorator.PydanticDecorator(ToolSessionConfiguration),
        nullable=False,
        default_factory=ToolSessionConfiguration,
    )

    versions: orm.Mapped[list[DatabaseVersion]] = orm.relationship(
        default_factory=list,
        back_populates="tool",
        cascade="all, delete-orphan",
    )
    natures: orm.Mapped[list[DatabaseNature]] = orm.relationship(
        default_factory=list,
        back_populates="tool",
        cascade="all, delete-orphan",
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

    compatible_versions: list[int] = pydantic.Field(
        default=[],
        description=lxml.etree.tostring(
            builder.HTML(
                builder.DIV(
                    "A list of tool version ids which are compatible with this tool. "
                    "You can provide version ids of the same tool or other tools. "
                    "When registering a tool version as compatible, the following behaviour will change: ",
                    builder.UL(
                        builder.LI(
                            "Models of compatible tool versions are available when requesting a provisioned session. "
                            "Let's illustrate this with an example: We have two tool versions A and B. "
                            "We add the tool version id of tool A to the compatible_versions list of tool B. "
                            "Now we can request a provisioned session of tool version B using a model of tool version A."
                        ),
                        builder.LI(
                            "TeamForCapella repositories will be loaded for all compatible tools. "
                        ),
                    ),
                    "Some examples of what this option can be used for: ",
                    builder.UL(
                        builder.LI(
                            "Define minor versions of a tool as compatible, e.g. Capella 7.0.0 and 7.0.1. "
                            "A provisioned Capella 7.0.1 can also load Capella 7.0.0 models."
                        ),
                        builder.LI(
                            "Define py-capellambse based tools as compatible with multiple versions of Capella. "
                            "py-capellambse can load multiple versions of Capella models. "
                        ),
                        builder.LI(
                            "Define individual versions of Capella + pure::variants as compatible with corresponding Capella versions. "
                            "In this case, TeamForCapella repositories will also be injected into Capella + pure::variants sessions. "
                        ),
                        builder.LI(
                            "Restrict a tool extensions to specific versions of another tool. "
                            "A tool extension might not be compatible with all versions of the tool it extends. "
                        ),
                    ),
                )
            ),
            encoding=str,
        ),
        examples=[[1, 2], []],
    )


class DatabaseVersion(database.Base):
    __tablename__ = "versions"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)

    name: orm.Mapped[str]

    tool_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tools.id"),
        init=False,
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(
        back_populates="versions"
    )

    config: orm.Mapped[ToolVersionConfiguration] = orm.mapped_column(
        decorator.PydanticDecorator(ToolVersionConfiguration),
        default_factory=ToolVersionConfiguration,
    )


class DatabaseNature(database.Base):
    __tablename__ = "types"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)
    name: orm.Mapped[str]

    tool_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tools.id"), init=False
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(back_populates="natures")


class CreateTool(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="forbid")

    name: str = pydantic.Field(default="", min_length=2, max_length=30)
    integrations: ToolIntegrations = pydantic.Field(default=ToolIntegrations())
    config: ToolSessionConfiguration = pydantic.Field(
        default=ToolSessionConfiguration()
    )


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
