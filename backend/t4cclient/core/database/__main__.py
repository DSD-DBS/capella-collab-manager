# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import pathlib

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from t4cclient.config import config
from t4cclient.core.database import Base, repositories, users
from t4cclient.schemas.repositories.users import Role

DATABASE_URL = config["database"]["url"]
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

LOGGER = logging.getLogger(__name__)


def migrate_db():
    if os.getenv("ALEMBIC_CONTEXT") != "1":
        root_dir = pathlib.Path(__file__).parents[2]

        # Get current revision of Database. If no revision is available, initialize the database.
        alembic_cfg = Config(root_dir / "alembic.ini")
        alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        alembic_cfg.attributes["configure_logger"] = False

        conn = engine.connect()

        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()

        if current_rev:
            LOGGER.info("Upgrade database to head")
            command.upgrade(alembic_cfg, "head")
        else:
            LOGGER.info("Empty database detected.")
            Base.metadata.create_all(bind=engine)
            LOGGER.info("Database structure creation successful")
            command.stamp(alembic_cfg, "head")
            initialize_admin_user()
            initialize_default_repository()


def initialize_admin_user():
    LOGGER.info("Initialized adminuser " + config["initial"]["admin"])
    with SessionLocal() as db:
        users.create_user(db=db, username=config["initial"]["admin"], role=Role.ADMIN)


def initialize_default_repository():
    LOGGER.info("Initialized repository 'default'")
    with SessionLocal() as db:
        repositories.create_repository(db=db, name="default")
