# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pydantic


def datetime_serializer(
    dt: datetime.datetime,
) -> datetime.datetime:
    return dt.replace(tzinfo=datetime.UTC)


def datetime_serializer_optional(
    dt: datetime.datetime | None,
) -> datetime.datetime | None:
    if dt is None:
        return None
    return datetime_serializer(dt)


class BaseModel(pydantic.BaseModel):
    """General pydantic base model.

    All pydantic models should inherit from this class.
    """

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        json_schema_serialization_defaults_required=True,
    )


class BaseModelStrict(pydantic.BaseModel):
    """Used for configuration models, which require a strict validation.

    Examples are models which are used in the YAML editor of the frontend.
    Here, the user should receive an error message if an unintended field is added.
    """

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        extra="forbid",
        json_schema_serialization_defaults_required=True,
    )
