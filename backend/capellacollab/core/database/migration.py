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

import capellacollab.projects.capellamodels.crud as models
import capellacollab.projects.capellamodels.modelsources.t4c.crud as t4c_models
import capellacollab.projects.crud as projects
import capellacollab.settings.modelsources.t4c.crud as t4c_instances
import capellacollab.settings.modelsources.t4c.repositories.crud as t4c_repositories
import capellacollab.tools.crud as tools
import capellacollab.users.crud as users
from capellacollab.config import config
from capellacollab.core.database import Base
from capellacollab.settings.modelsources.t4c.models import (
    DatabaseT4CInstance,
    Protocol,
)
from capellacollab.settings.modelsources.t4c.repositories.models import (
    CreateT4CRepository,
)
from capellacollab.tools.models import Tool
from capellacollab.users.models import Role

LOGGER = logging.getLogger(__name__)


def migrate_db(engine):
    if os.getenv("ALEMBIC_CONTEXT") != "1":
        os.environ["ALEMBIC_CONFIGURE_LOGGER"] = "false"
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
        repositories_exist = inspect(engine).has_table("t4c_repositories")
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

            if not repositories_exist:
                create_t4c_instance_and_repositories(session)


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
        docker_image_template=f"{registry}/t4c/client/remote:$version-latest",
        docker_image_backup_template=f"{registry}/t4c/client/backup:$version-latest",
        readonly_docker_image_template=f"{registry}/capella/readonly:$version-latest",
    )
    papyrus = Tool(
        name="Papyrus",
        docker_image_template=f"{registry}/papyrus/client/remote:$version-prod",
    )
    tools.create_tool(db, capella)
    tools.create_tool(db, papyrus)

    default_version = tools.create_version(db, capella.id, "6.0.0", True)
    tools.create_version(db, capella.id, "5.2.0")
    tools.create_version(db, capella.id, "5.0.0")

    tools.create_version(db, papyrus.id, "6.1")
    tools.create_version(db, papyrus.id, "6.0")

    default_nature = tools.create_nature(db, capella.id, "model")
    tools.create_nature(db, capella.id, "library")

    tools.create_nature(db, papyrus.id, "UML 2.5")
    tools.create_nature(db, papyrus.id, "SysML 1.4")
    tools.create_nature(db, papyrus.id, "SysML 1.1")

    for model in models.get_all_models(db):
        models.set_tool_for_model(db, model, capella)
        models.set_tool_details_for_model(
            db, model, default_version, default_nature
        )


def create_t4c_instance_and_repositories(db):
    LOGGER.info("Initialized T4C instance and repositories")
    tool = tools.get_tool_by_name(db, "Capella")
    version = tools.get_version_by_name(db, tool, "5.2.0")
    default_instance = DatabaseT4CInstance(
        name="default",
        license="placeholder",
        protocol=Protocol.tcp,
        host="localhost",
        port=2036,
        cdo_port=12036,
        usage_api="http://localhost:8086",
        rest_api="http://localhost:8081/api/v1.0",
        username="admin",
        password="password",
        version=version,
    )
    t4c_instances.create_t4c_instance(default_instance, db)
    for t4c_model in t4c_models.get_all_t4c_models(db):
        repository = CreateT4CRepository(
            name=t4c_model.name,
        )
        t4c_repository = t4c_repositories.create_t4c_repository(
            repository, default_instance, db
        )
        t4c_models.set_repository_for_t4c_model(db, t4c_model, t4c_repository)
