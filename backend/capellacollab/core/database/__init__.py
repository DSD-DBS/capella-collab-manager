# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import functools
import json
import typing as t

import pydantic
import sqlalchemy as sa
import valkey
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

from capellacollab.configuration.app import config


def json_serializer(value):
    def _default(val):
        if isinstance(val, set):
            return list(val)

        raise TypeError(f"Object of type {type(val)} is not JSON serializable")

    return json.dumps(value, default=_default)


engine = sa.create_engine(
    config.database.url,
    connect_args={"connect_timeout": 5, "options": "-c timezone=utc"},
    pool_size=20,
    pool_timeout=5,
    json_serializer=json_serializer,
)
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(orm.MappedAsDataclass, orm.DeclarativeBase):
    type_annotation_map = {
        dict["str", "str"]: postgresql.JSONB,
        dict[str, str]: postgresql.JSONB,
        dict[str, t.Any]: postgresql.JSONB,
        dict[str, bool]: postgresql.JSONB,
    }


### SQL MODELS ARE IMPORTED HERE ###
# ruff: noqa: F401
from . import models  # isort:skip


def get_db() -> t.Iterator[orm.Session]:
    with SessionLocal() as session:
        yield session


@functools.lru_cache
def get_valkey() -> valkey.Valkey:
    return valkey.Valkey.from_url(config.valkey.url, decode_responses=True)


def patch_database_with_pydantic_object(
    database_object: Base, pydantic_object: pydantic.BaseModel
):
    for key, value in pydantic_object.model_dump().items():
        if value is not None:
            setattr(database_object, key, value)


def validate_database_session(db: orm.Session) -> bool:
    try:
        db.connection()
        return True
    except BaseException:
        return False
