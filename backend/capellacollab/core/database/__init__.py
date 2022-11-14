# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from capellacollab.config import config

engine = create_engine(
    config["database"]["url"], connect_args={"connect_timeout": 5}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

### SQL MODELS ARE IMPORTED HERE ###
from . import models  # isort:skip


def get_db() -> Session:
    with SessionLocal() as session:
        yield session
