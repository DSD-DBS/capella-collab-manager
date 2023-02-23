# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib

import sqlalchemy
from alembic import command
from alembic import config as alembic_config
from alembic import migration
from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core import database
from capellacollab.projects import crud as projects_crud
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import crud as settings_t4c_crud
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as repositories_crud,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    models as settings_repositories_models,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models
from capellacollab.users.events import crud as events_crud

LOGGER = logging.getLogger(__name__)


def migrate_db(engine, database_url: str):
    if os.getenv("ALEMBIC_CONTEXT") != "1":
        os.environ["ALEMBIC_CONFIGURE_LOGGER"] = "false"
        root_dir = pathlib.Path(__file__).parents[2]

        # Get current revision of Database. If no revision is available, initialize the database.

        alembic_cfg = alembic_config.Config(str(root_dir / "alembic.ini"))
        alembic_cfg.set_main_option(
            "script_location", str(root_dir / "alembic")
        )
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        alembic_cfg.attributes[  # pylint:disable=unsupported-assignment-operation
            "configure_logger"
        ] = False

        with engine.connect() as conn:
            context = migration.MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

        tools_exist = sqlalchemy.inspect(engine).has_table("tools")
        repositories_exist = sqlalchemy.inspect(engine).has_table(
            "t4c_repositories"
        )
        session_maker = orm.sessionmaker(bind=engine)

        with session_maker() as session:
            if current_rev:
                LOGGER.info("Upgrade database to head")
                command.upgrade(alembic_cfg, "head")
            else:
                LOGGER.info("Empty database detected.")
                database.Base.metadata.create_all(bind=engine)
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
    admin_user = users_crud.create_user(
        db=db,
        username=config["initial"]["admin"],
        role=users_models.Role.ADMIN,
    )
    events_crud.create_user_creation_event(db, admin_user)


def initialize_default_project(db):
    LOGGER.info("Initialized project 'default'")
    projects_crud.create_project(db=db, name="default")


def create_tools(db):
    LOGGER.info("Initialized tools")
    registry = config["docker"]["registry"]
    capella = tools_models.Tool(
        name="Capella",
        docker_image_template=f"{registry}/capella/remote:$version-latest",
        docker_image_backup_template=f"{registry}/t4c/client/backup:$version-latest",
        readonly_docker_image_template=f"{registry}/capella/readonly:$version-latest",
    )
    papyrus = tools_models.Tool(
        name="Papyrus",
        docker_image_template=f"{registry}/papyrus/client/remote:$version-prod",
    )
    tools_crud.create_tool(db, capella)
    tools_crud.create_tool(db, papyrus)

    default_version = tools_crud.create_version(db, capella.id, "6.0.0", True)
    tools_crud.create_version(db, capella.id, "5.2.0")
    tools_crud.create_version(db, capella.id, "5.0.0")

    tools_crud.create_version(db, papyrus.id, "6.1")
    tools_crud.create_version(db, papyrus.id, "6.0")

    default_nature = tools_crud.create_nature(db, capella.id, "model")
    tools_crud.create_nature(db, capella.id, "library")

    tools_crud.create_nature(db, papyrus.id, "UML 2.5")
    tools_crud.create_nature(db, papyrus.id, "SysML 1.4")
    tools_crud.create_nature(db, papyrus.id, "SysML 1.1")

    for model in toolmodels_crud.get_all_models(db):
        toolmodels_crud.set_tool_for_model(db, model, capella)
        toolmodels_crud.set_tool_details_for_model(
            db, model, default_version, default_nature
        )


def create_t4c_instance_and_repositories(db):
    LOGGER.info("Initialized T4C instance and repositories")
    tool = tools_crud.get_tool_by_name(db, "Capella")
    version = tools_crud.get_version_by_name(db, tool, "5.2.0")
    default_instance = settings_t4c_models.DatabaseT4CInstance(
        name="default",
        license="placeholder",
        protocol=settings_t4c_models.Protocol.tcp,
        host="localhost",
        port=2036,
        cdo_port=12036,
        usage_api="http://localhost:8086",
        rest_api="http://localhost:8081/api/v1.0",
        username="admin",
        password="password",
        version=version,
    )
    settings_t4c_crud.create_t4c_instance(default_instance, db)
    for t4c_model in t4c_crud.get_t4c_models(db):
        repository = settings_repositories_models.CreateT4CRepository(
            name=t4c_model.name,
        )
        t4c_repository = repositories_crud.create_t4c_repository(
            repository, default_instance, db
        )
        t4c_crud.set_repository_for_t4c_model(db, t4c_model, t4c_repository)
