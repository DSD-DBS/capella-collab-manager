# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib

from alembic import command
from alembic import config as alembic_config
from alembic import migration
from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core import database
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as project_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import crud as git_crud
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import crud as settings_t4c_crud
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)
from capellacollab.settings.modelsources.t4c.repositories import (
    crud as repositories_crud,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.tools.integrations import crud as integrations_crud
from capellacollab.tools.integrations import models as integrations_models
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
        alembic_cfg.attributes["configure_logger"] = False

        with engine.connect() as conn:
            context = migration.MigrationContext.configure(conn)
            current_rev = context.get_current_revision()

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

                create_tools(session)
                create_t4c_instance_and_repositories(session)
                create_models(session)


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
    projects_crud.create_project(
        db=db,
        name="default",
        description="",
        visibility=project_models.Visibility.INTERNAL,
    )


def create_tools(db):
    LOGGER.info("Initialized tools")
    registry = config["docker"]["registry"]
    if os.getenv("DEVELOPMENT_MODE", "").lower() in ("1", "true", "t"):
        capella = tools_models.DatabaseTool(
            name="Capella",
            docker_image_template=f"{registry}/capella/remote:$version-latest",
            docker_image_backup_template=f"{registry}/t4c/client/base:$version-latest",
            readonly_docker_image_template=f"{registry}/capella/readonly:$version-latest",
        )

        papyrus = tools_models.DatabaseTool(
            name="Papyrus",
            docker_image_template=f"{registry}/papyrus/client/remote:$version-prod",
        )
        tools_crud.create_tool(db, papyrus)

        tools_crud.create_version(db, papyrus.id, "6.1")
        tools_crud.create_version(db, papyrus.id, "6.0")

        tools_crud.create_nature(db, papyrus.id, "UML 2.5")
        tools_crud.create_nature(db, papyrus.id, "SysML 1.4")
        tools_crud.create_nature(db, papyrus.id, "SysML 1.1")

    else:
        # Use public Github images per default
        capella = tools_models.DatabaseTool(
            name="Capella",
            docker_image_template="ghcr.io/dsd-dbs/capella-dockerimages/capella/remote:$version-selected-dropins-main",
            docker_image_backup_template="",
            readonly_docker_image_template="ghcr.io/dsd-dbs/capella-dockerimages/capella/readonly:$version-selected-dropins-main",
        )

    tools_crud.create_tool(db, capella)

    jupyter = tools_models.DatabaseTool(
        name="Jupyter",
        docker_image_template=f"{registry}/jupyter-notebook:$version",
    )
    tools_crud.create_tool(db, jupyter)
    integrations_crud.update_integrations(
        db,
        jupyter.integrations,
        integrations_models.PatchToolIntegrations(jupyter=True),
    )

    default_version = tools_crud.create_version(db, capella.id, "6.0.0", True)
    tools_crud.create_version(db, capella.id, "5.2.0")
    tools_crud.create_version(db, capella.id, "5.0.0")

    tools_crud.create_version(db, jupyter.id, "python-3.11")
    tools_crud.create_nature(db, jupyter.id, "notebooks")

    default_nature = tools_crud.create_nature(db, capella.id, "model")
    tools_crud.create_nature(db, capella.id, "library")

    for model in toolmodels_crud.get_models(db):
        toolmodels_crud.set_tool_for_model(db, model, capella)
        toolmodels_crud.set_tool_details_for_model(
            db, model, default_version, default_nature
        )


def create_t4c_instance_and_repositories(db):
    tool = tools_crud.get_tool_by_name(db, "Capella")
    assert tool

    version = tools_crud.get_version_by_tool_id_version_name(
        db, tool.id, "5.2.0"
    )
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
    settings_t4c_crud.create_t4c_instance(db, default_instance)
    for t4c_model in t4c_crud.get_t4c_models(db):
        t4c_model.repository = repositories_crud.create_t4c_repository(
            db=db, repo_name=t4c_model.name, instance=default_instance
        )
        db.commit()
    LOGGER.info("Initialized T4C instance and repositories")


def create_models(db: orm.Session):
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    default_project = projects_crud.get_project_by_slug(db, "default")
    assert default_project

    for version in ["5.0.0", "5.2.0", "6.0.0"]:
        capella_model = toolmodels_crud.create_model(
            db=db,
            project=default_project,
            post_model=toolmodels_models.PostCapellaModel(
                name=f"Melody Model Test {version}",
                description="",
                tool_id=capella_tool.id,
            ),
            tool=capella_tool,
            version=tools_crud.get_version_by_tool_id_version_name(
                db, capella_tool.id, version
            ),
            nature=tools_crud.get_nature_by_name(db, capella_tool, "model"),
        )

        git_crud.add_git_model_to_capellamodel(
            db=db,
            capella_model=capella_model,
            post_git_model=git_models.PostGitModel(
                path="https://github.com/DSD-DBS/py-capellambse",
                entrypoint=f'/tests/data/melodymodel/{version[:3].replace(".", "_")}/Melody Model Test.aird',
                revision="master",
                username="",
                password="",
            ),
        )
    LOGGER.info("Initialized default models")
