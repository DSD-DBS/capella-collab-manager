# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import logging
import os
import pathlib

# 3rd party:
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1st party:
import capellacollab.projects.crud as projects
from capellacollab.config import config
from capellacollab.core.database import Base, users
from capellacollab.projects.users.models import Role

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
        projects.create_project(db=db, name="default")
