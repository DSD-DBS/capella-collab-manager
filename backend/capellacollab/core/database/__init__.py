# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from capellacollab.config import config

engine = create_engine(
    config["database"]["url"], connect_args={"connect_timeout": 5}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


### SQL MODELS ARE IMPORTED HERE ###
from . import models  # isort:skip # pylint: disable=unused-import


def get_db() -> Session:
    with SessionLocal() as session:
        yield session


def patch_database_with_pydantic_object(
    database_object: Base, pydantic_object: BaseModel
):
    for key, value in pydantic_object.dict().items():
        if value is not None:
            setattr(database_object, key, value)
