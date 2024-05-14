# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic


class DatabaseConfiguration(database.Base):
    __tablename__ = "configuration"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, unique=True, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    configuration: orm.Mapped[dict[str, t.Any]]


class MetadataConfiguration(core_pydantic.BaseModelStrict):
    privacy_policy_url: str = pydantic.Field(
        default="https://example.com/privacy"
    )
    imprint_url: str = pydantic.Field(default="https://example.com/imprint")
    provider: str = pydantic.Field(
        default="Systems Engineering Toolchain team"
    )
    authentication_provider: str = pydantic.Field(
        default="OAuth2",
        description="Authentication provides which is displayed in the frontend.",
    )
    environment: str = pydantic.Field(default="-", description="general")


class ConfigurationBase(core_pydantic.BaseModelStrict, abc.ABC):
    """
    Base class for configuration models. Can be used to define new configurations
    in the future.
    """

    _name: t.ClassVar[str]


class GlobalConfiguration(ConfigurationBase):
    """Global application configuration."""

    _name: t.ClassVar[t.Literal["global"]] = "global"

    metadata: MetadataConfiguration = pydantic.Field(
        default_factory=MetadataConfiguration
    )


# All subclasses of ConfigurationBase are automatically registered using this dict.
NAME_TO_MODEL_TYPE_MAPPING: dict[str, t.Type[ConfigurationBase]] = {
    model()._name: model for model in ConfigurationBase.__subclasses__()
}
