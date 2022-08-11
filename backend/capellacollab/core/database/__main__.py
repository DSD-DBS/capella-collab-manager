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
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# 1st party:
import capellacollab.projects.crud as projects
import capellacollab.tools.crud as tools
from capellacollab.config import config
from capellacollab.core.database import Base, users
from capellacollab.projects.users.models import Role
from capellacollab.tools.models import Tool

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
        tools_exist = inspect(engine).has_table("tools")

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

        if not tools_exist:
            create_tools()


def initialize_admin_user():
    LOGGER.info("Initialized adminuser " + config["initial"]["admin"])
    with SessionLocal() as db:
        users.create_user(db=db, username=config["initial"]["admin"], role=Role.ADMIN)


def initialize_default_repository():
    LOGGER.info("Initialized repository 'default'")
    with SessionLocal() as db:
        projects.create_project(db=db, name="default")


def create_tools():
    LOGGER.info("Initialized tools")
    with SessionLocal() as db:
        capella = Tool(
            name="Capella", docker_image_template="/t4c/client/remote/$version:prod"
        )
        papyrus = Tool(
            name="Papyrus", docker_image_template="/papyrus/client/remote/$version:prod"
        )
        tools.create_tool(db, capella)
        tools.create_tool(db, papyrus)

        tools.create_version(db, capella.id, "6.2", True)
        tools.create_version(db, capella.id, "6.0")
        tools.create_version(db, capella.id, "5.2")

        tools.create_version(db, papyrus.id, "6.2")
        tools.create_version(db, papyrus.id, "6.0")

        tools.create_type(db, capella.id, "model")
        tools.create_type(db, capella.id, "library")

        tools.create_type(db, papyrus.id, "UML 2.5")
        tools.create_type(db, papyrus.id, "SysML 1.4")
        tools.create_type(db, papyrus.id, "SysML 1.1")
