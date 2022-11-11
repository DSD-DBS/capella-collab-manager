# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

import capellacollab.projects.crud as projects
import capellacollab.tools.crud as tools
import capellacollab.users.crud as users
from capellacollab.config import config
from capellacollab.core.database import Base
from capellacollab.tools.models import Tool
from capellacollab.users.models import Role

LOGGER = logging.getLogger(__name__)


def migrate_db(engine):
    if os.getenv("ALEMBIC_CONTEXT") != "1":
        root_dir = pathlib.Path(__file__).parents[2]

        # Get current revision of Database. If no revision is available, initialize the database.
        alembic_cfg = Config(root_dir / "alembic.ini")
        alembic_cfg.set_main_option(
            "script_location", str(root_dir / "alembic")
        )
        alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))
        alembic_cfg.attributes["configure_logger"] = False

        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        tools_exist = inspect(engine).has_table("tools")
        session_maker = sessionmaker(bind=engine)

        with session_maker() as session:
            if current_rev:
                LOGGER.info("Upgrade database to head")
                command.upgrade(alembic_cfg, "head")
            else:
                LOGGER.info("Empty database detected.")
                Base.metadata.create_all(bind=engine)
                LOGGER.info("Database structure creation successful")
                command.stamp(alembic_cfg, "head")
                initialize_admin_user(session)
                initialize_default_project(session)

            if not tools_exist:
                create_tools(session)


def initialize_admin_user(db):
    LOGGER.info("Initialized adminuser %s", config["initial"]["admin"])
    users.create_user(
        db=db, username=config["initial"]["admin"], role=Role.ADMIN
    )


def initialize_default_project(db):
    LOGGER.info("Initialized project 'default'")
    projects.create_project(db=db, name="default")


def create_tools(db):
    LOGGER.info("Initialized tools")
    registry = config["docker"]["registry"]
    capella = Tool(
        name="Capella",
        docker_image_template=f"{registry}/t4c/client/remote/$version:prod",
        readonly_docker_image_template=f"{registry}/capella/readonly/$version:prod",
    )
    papyrus = Tool(
        name="Papyrus",
        docker_image_template=f"{registry}/papyrus/client/remote/$version:prod",
    )
    tools.create_tool(db, capella)
    tools.create_tool(db, papyrus)

    tools.create_version(db, capella.id, "6.0", True)
    tools.create_version(db, capella.id, "5.2")
    tools.create_version(db, capella.id, "5.0")

    tools.create_version(db, papyrus.id, "6.1")
    tools.create_version(db, papyrus.id, "6.0")

    tools.create_nature(db, capella.id, "model")
    tools.create_nature(db, capella.id, "library")

    tools.create_nature(db, papyrus.id, "UML 2.5")
    tools.create_nature(db, papyrus.id, "SysML 1.4")
    tools.create_nature(db, papyrus.id, "SysML 1.1")
