# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib

from alembic import command
from alembic import config as alembic_config
from alembic import migration
from sqlalchemy import orm

from capellacollab import core
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.events import crud as events_crud
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as project_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import crud as git_crud
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.settings.modelsources.git import crud as modelsources_crud
from capellacollab.settings.modelsources.git import (
    models as modelsources_models,
)
from capellacollab.settings.modelsources.t4c.instance import (
    crud as t4c_instance_crud,
)
from capellacollab.settings.modelsources.t4c.instance import (
    models as t4c_instance_models,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    crud as t4c_license_server_crud,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    models as t4c_license_server_models,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

LOGGER = logging.getLogger(__name__)


def migrate_db(engine, database_url: str):
    if os.getenv("ALEMBIC_CONTEXT") == "1":
        return

    os.environ["ALEMBIC_CONFIGURE_LOGGER"] = "false"
    root_dir = pathlib.Path(__file__).parents[2]

    # Get current revision of Database. If no revision is available, initialize the database.

    alembic_cfg = alembic_config.Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
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
            initialize_coffee_machine_project(session)

            create_tools(session)
            create_t4c_instance_and_repositories(session)
            create_git_instances(session)
            create_default_models(session)
            create_coffee_machine_model(session)

    logging.info("Database migrations completed.")


def initialize_admin_user(db: orm.Session):
    LOGGER.info("Initialized adminuser %s", config.initial.admin)
    admin_user = users_crud.create_user(
        db=db,
        username=config.initial.admin,
        idp_identifier=config.initial.admin,
        role=users_models.Role.ADMIN,
    )
    events_crud.create_user_creation_event(db, admin_user)


def initialize_default_project(db: orm.Session):
    LOGGER.info("Initialized project 'default'")
    projects_crud.create_project(
        db=db,
        name="default",
        description="",
        visibility=project_models.Visibility.INTERNAL,
    )


def initialize_coffee_machine_project(db: orm.Session):
    LOGGER.info("Initialize project 'Coffee Machine'")
    projects_crud.create_project(
        db=db,
        name="Coffee Machine",
        description="",
        visibility=project_models.Visibility.INTERNAL,
    )


def get_eclipse_session_configuration() -> (
    tools_models.ToolSessionConfiguration
):
    """Returns the session configuration for Eclipse based tools
    in the Capella Dockerimages repository.
    """
    return tools_models.ToolSessionConfiguration(
        resources=tools_models.Resources(
            cpu=tools_models.CPUResources(requests=0.4, limits=2),
            memory=tools_models.MemoryResources(
                requests="1.6Gi", limits="6Gi"
            ),
        ),
        environment={
            "RMT_PASSWORD": "{CAPELLACOLLAB_SESSION_TOKEN}",
            "ECLIPSE_PROJECTS_TO_LOAD": "{CAPELLACOLLAB_SESSION_PROVISIONING}",
        },
        connection=tools_models.ToolSessionConnection(
            methods=[
                tools_models.GuacamoleConnectionMethod(
                    id="guacamole",
                    name="Guacamole",
                    description="Guacamole doesn't support session sharing.",
                    ports=tools_models.RDPPorts(metrics=9118, rdp=3389),
                    environment={"CONNECTION_METHOD": "xrdp"},
                ),
                tools_models.HTTPConnectionMethod(
                    id="xpra",
                    name="Xpra",
                    description="Xpra supports session sharing.",
                    ports=tools_models.HTTPPorts(http=10000, metrics=9118),
                    environment={
                        "CONNECTION_METHOD": "xpra",
                        "XPRA_SUBPATH": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
                        "XPRA_CSP_ORIGIN_HOST": "{CAPELLACOLLAB_ORIGIN_BASE_URL}",
                    },
                    redirect_url=(
                        (
                            "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}"
                            if not core.LOCAL_DEVELOPMENT_MODE
                            else "http://localhost:8080"
                        )
                        + "{CAPELLACOLLAB_SESSIONS_BASE_PATH}/?floating_menu=0&sharing=1&path={CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
                    ),
                    cookies={},
                    sharing=tools_models.ToolSessionSharingConfiguration(
                        enabled=True
                    ),
                ),
            ]
        ),
        provisioning=tools_models.ToolModelProvisioning(
            directory="/models",
        ),
    )


def create_capella_tool(db: orm.Session) -> tools_models.DatabaseTool:
    registry: str = config.docker.sessions_registry

    capella = tools_models.CreateTool(
        name="Capella",
        integrations=tools_models.ToolIntegrations(
            t4c=True, pure_variants=False, jupyter=False
        ),
        config=get_eclipse_session_configuration(),
    )
    capella_database = tools_crud.create_tool(db, capella)

    for capella_version_name in ("5.0.0", "5.2.0", "6.0.0", "6.1.0", "7.0.0"):
        # pylint: disable=unsupported-membership-test
        if "localhost" in registry:
            docker_tag = f"{capella_version_name}-latest"
        else:
            docker_tag = f"{capella_version_name}-selected-dropins-main"

        capella_version = tools_models.CreateToolVersion(
            name=capella_version_name,
            config=tools_models.ToolVersionConfiguration(
                is_recommended=capella_version_name == "7.0.0",
                is_deprecated=capella_version_name in ("5.0.0", "5.2.0"),
                sessions=tools_models.SessionToolConfiguration(
                    persistent=tools_models.PersistentSessionToolConfiguration(
                        image=tools_models.PersistentSessionToolConfigurationImages(
                            regular=f"{registry}/capella/remote:{docker_tag}",
                            beta=None,
                        ),
                    ),
                ),
                backups=tools_models.ToolBackupConfiguration(
                    image=f"{registry}/t4c/client/base:{docker_tag}"
                ),
            ),
        )
        tools_crud.create_version(
            db,
            capella_database,
            capella_version,
        )

    tools_crud.create_nature(db, capella_database, "model")
    tools_crud.create_nature(db, capella_database, "library")

    return capella_database


def create_papyrus_tool(db: orm.Session) -> tools_models.DatabaseTool:
    papyrus = tools_models.CreateTool(
        name="Papyrus",
        integrations=tools_models.ToolIntegrations(
            t4c=False, pure_variants=False, jupyter=False
        ),
        config=get_eclipse_session_configuration(),
    )
    papyrus_database = tools_crud.create_tool(db, papyrus)

    for papyrus_version_name in ("6.0", "6.1"):
        papyrus_version = tools_models.CreateToolVersion(
            name=papyrus_version_name,
            config=tools_models.ToolVersionConfiguration(
                is_recommended=False,
                is_deprecated=False,
                sessions=tools_models.SessionToolConfiguration(
                    persistent=tools_models.PersistentSessionToolConfiguration(
                        image=tools_models.PersistentSessionToolConfigurationImages(
                            regular=f"{config.docker.sessions_registry}/papyrus/remote:{papyrus_version_name}-latest",
                            beta=None,
                        ),
                    ),
                ),
                backups=tools_models.ToolBackupConfiguration(image=None),
            ),
        )

        tools_crud.create_version(
            db,
            papyrus_database,
            papyrus_version,
        )

    tools_crud.create_nature(db, papyrus_database, "UML 2.5")
    tools_crud.create_nature(db, papyrus_database, "SysML 1.4")
    tools_crud.create_nature(db, papyrus_database, "SysML 1.1")

    return papyrus_database


def create_jupyter_tool(db: orm.Session) -> tools_models.DatabaseTool:
    jupyter = tools_models.CreateTool(
        name="Jupyter",
        integrations=tools_models.ToolIntegrations(jupyter=True),
        config=tools_models.ToolSessionConfiguration(
            resources=tools_models.Resources(
                cpu=tools_models.CPUResources(requests=1, limits=2),
                memory=tools_models.MemoryResources(
                    requests="500Mi", limits="3Gi"
                ),
            ),
            environment={
                "JUPYTER_PORT": "8888",
                "JUPYTER_TOKEN": "{CAPELLACOLLAB_SESSION_TOKEN}",
                "CSP_ORIGIN_HOST": "{CAPELLACOLLAB_ORIGIN_BASE_URL}",
                "JUPYTER_BASE_URL": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
            },
            connection=tools_models.ToolSessionConnection(
                methods=[
                    tools_models.HTTPConnectionMethod(
                        id="jupyter-direct",
                        name="Direct Jupyter connection (Browser)",
                        description="The only available connection method for Jupyter.",
                        ports=tools_models.HTTPPorts(http=8888, metrics=9118),
                        redirect_url=(
                            (
                                "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}"
                                if not core.LOCAL_DEVELOPMENT_MODE
                                else "http://localhost:8080"
                            )
                            + "{CAPELLACOLLAB_SESSIONS_BASE_PATH}/lab?token={CAPELLACOLLAB_SESSION_TOKEN}"
                        ),
                        sharing=tools_models.ToolSessionSharingConfiguration(
                            enabled=True
                        ),
                    ),
                ]
            ),
            monitoring=tools_models.SessionMonitoring(
                prometheus=tools_models.PrometheusConfiguration(
                    path="/prometheus"
                )
            ),
            provisioning=tools_models.ToolModelProvisioning(
                directory="/models",
            ),
        ),
    )
    jupyter_database = tools_crud.create_tool(db, jupyter)

    tools_crud.create_version(
        db,
        jupyter_database,
        tools_models.CreateToolVersion(
            name="python-3.11",
            config=tools_models.ToolVersionConfiguration(
                is_recommended=False,
                is_deprecated=False,
                sessions=tools_models.SessionToolConfiguration(
                    persistent=tools_models.PersistentSessionToolConfiguration(
                        image=tools_models.PersistentSessionToolConfigurationImages(
                            regular=f"{config.docker.sessions_registry}/jupyter-notebook:python-3.11",
                            beta=None,
                        ),
                    ),
                ),
                backups=tools_models.ToolBackupConfiguration(image=None),
            ),
        ),
    )

    tools_crud.create_nature(db, jupyter_database, "notebooks")

    return jupyter_database


def create_tools(db: orm.Session):
    create_capella_tool(db)

    # pylint: disable=unsupported-membership-test
    if "localhost" in config.docker.sessions_registry:
        create_papyrus_tool(db)
        create_jupyter_tool(db)

    LOGGER.info("Initialized tools")


def create_t4c_instance_and_repositories(db):
    tool = tools_crud.get_tool_by_name(db, "Capella")
    assert tool

    version = tools_crud.get_version_by_tool_id_version_name(
        db, tool.id, "7.0.0"
    )
    assert version

    _create_local_t4c_environment(db, version)
    _create_cluster_t4c_environment(db, version)
    LOGGER.info("Initialized T4C instance and repositories")


def _create_local_t4c_environment(
    db: orm.Session, version: tools_models.DatabaseVersion
):
    local_license_server = t4c_license_server_models.DatabaseT4CLicenseServer(
        name="Local license server",
        usage_api="http://localhost:8086",
        license_key="Placeholder",
    )
    t4c_license_server_crud.create_t4c_license_server(db, local_license_server)

    local_instance = t4c_instance_models.DatabaseT4CInstance(
        name="Local server",
        protocol=t4c_instance_models.Protocol.tcp,
        host="localhost",
        port=2036,
        cdo_port=12036,
        http_port=8080,
        license_server=local_license_server,
        rest_api="http://localhost:8081/api/v1.0",
        username="admin",
        password="password",
        version=version,
    )
    t4c_instance_crud.create_t4c_instance(db, local_instance)


def _create_cluster_t4c_environment(
    db: orm.Session, version: tools_models.DatabaseVersion
):
    cluster_license_server = (
        t4c_license_server_models.DatabaseT4CLicenseServer(
            name="Cluster-internal license server",
            usage_api="http://dev-license-server.t4c.svc.cluster.local:8086",
            license_key="Placeholder",
        )
    )
    t4c_license_server_crud.create_t4c_license_server(
        db, cluster_license_server
    )

    cluster_instance = t4c_instance_models.DatabaseT4CInstance(
        name="Cluster-internal server",
        protocol=t4c_instance_models.Protocol.ws,
        host="dev-server-internal.t4c.svc.cluster.local",
        port=2036,
        cdo_port=12036,
        http_port=8080,
        license_server=cluster_license_server,
        rest_api="http://dev-server-internal.t4c.svc.cluster.local:8080/api/v1.0",
        username="admin",
        password="password",
        version=version,
    )
    t4c_instance_crud.create_t4c_instance(db, cluster_instance)


def create_git_instances(db: orm.Session):
    modelsources_crud.create_git_instance(
        db=db,
        body=modelsources_models.PostGitInstance(
            type=modelsources_models.GitType.GITLAB,
            name="GitLab",
            url="https://gitlab.com",
            api_url="https://gitlab.com/api/v4",
        ),
    )
    modelsources_crud.create_git_instance(
        db=db,
        body=modelsources_models.PostGitInstance(
            type=modelsources_models.GitType.GITHUB,
            name="GitHub",
            url="https://github.com",
            api_url="https://api.github.com",
        ),
    )


def create_default_models(db: orm.Session):
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    default_project = projects_crud.get_project_by_slug(db, "default")
    assert default_project

    for version in ["5.0.0", "5.2.0", "6.0.0"]:
        capella_model = toolmodels_crud.create_model(
            db=db,
            project=default_project,
            post_model=toolmodels_models.PostToolModel(
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


def create_coffee_machine_model(db: orm.Session):
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    coffee_machine_project = projects_crud.get_project_by_slug(
        db, "coffee-machine"
    )
    assert coffee_machine_project

    capella_model = toolmodels_crud.create_model(
        db=db,
        project=coffee_machine_project,
        post_model=toolmodels_models.PostToolModel(
            name="Coffee Machine",
            description="An open source model of a coffee machine",
            tool_id=capella_tool.id,
        ),
        tool=capella_tool,
        version=tools_crud.get_version_by_tool_id_version_name(
            db, capella_tool.id, "6.0.0"
        ),
        nature=tools_crud.get_nature_by_name(db, capella_tool, "model"),
    )

    git_crud.add_git_model_to_capellamodel(
        db=db,
        capella_model=capella_model,
        post_git_model=git_models.PostGitModel(
            path="https://github.com/DSD-DBS/coffee-machine",
            entrypoint="coffee-machine-demo.aird",
            revision="main",
            username="",
            password="",
        ),
    )
    LOGGER.info("Initialized coffee machine model")
