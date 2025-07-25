# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib

from alembic import command, migration
from alembic import config as alembic_config
from sqlalchemy import orm

from capellacollab import core
from capellacollab.announcements import crud as announcements_crud
from capellacollab.announcements import models as announcements_models
from capellacollab.configuration.app import config
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

logger = logging.getLogger(__name__)

DEFAULT_REDIRECT_URL = (
    "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}"
    if not core.LOCAL_DEVELOPMENT_MODE
    else "http://localhost:8080"
)


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
            logger.info("Upgrade database to head")
            command.upgrade(alembic_cfg, "head")
        else:
            logger.info("Empty database detected.")
            database.Base.metadata.create_all(bind=engine)
            logger.info("Database structure creation successful")
            command.stamp(alembic_cfg, "head")
            initialize_admin_user(session)
            create_welcome_announcement(session)
            create_tools(session)

            initialize_capellambse_test_project(session)
            initialize_coffee_machine_project(session)
            initialize_ife_project(session)

            create_t4c_instance_and_repositories(session)
            create_git_instances(session)

    logger.info("Database migrations completed.")


def initialize_admin_user(db: orm.Session):
    admin_user = users_crud.create_user(
        db=db,
        username=config.initial.admin,
        idp_identifier=config.initial.admin,
        role=users_models.Role.ADMIN,
    )
    events_crud.create_user_creation_event(db, admin_user)
    logger.info("Initialized admin user %s", config.initial.admin)


def create_welcome_announcement(db: orm.Session):
    welcome_announcement = announcements_crud.create_announcement(
        db,
        announcements_models.CreateAnnouncementRequest(
            title="Welcome to the Capella Collaboration Manager",
            message="Make sure to check out our documentation to learn more",
            level=announcements_models.AnnouncementLevel.PRIMARY,
            dismissible=True,
        ),
    )
    logger.info("Initialized welcome announcement %s", welcome_announcement.id)


def initialize_capellambse_test_project(db: orm.Session):
    project = projects_crud.create_project(
        db=db,
        name="Melody Model Test",
        description="Group of test models of the capellambse Python library",
        visibility=project_models.ProjectVisibility.INTERNAL,
    )
    create_capellambse_test_models(db, project)
    logger.info("Initialized project '%s'", project.name)


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
                        DEFAULT_REDIRECT_URL
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


def create_capella_tool(
    db: orm.Session,
) -> tuple[tools_models.DatabaseTool, list[tools_models.DatabaseVersion]]:
    registry: str = config.docker.sessions_registry

    capella = tools_models.CreateTool(
        name="Capella",
        integrations=tools_models.ToolIntegrations(
            t4c=True, pure_variants=False
        ),
        config=get_eclipse_session_configuration(),
    )
    capella_database = tools_crud.create_tool(db, capella)

    capella_versions = []
    for capella_version_name in ("5.0.0", "5.2.0", "6.0.0", "6.1.0", "7.0.0"):
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
        capella_versions.append(
            tools_crud.create_version(
                db,
                capella_database,
                capella_version,
            )
        )

    tools_crud.create_nature(db, capella_database, "model")
    tools_crud.create_nature(db, capella_database, "library")

    return capella_database, capella_versions


def create_capella_model_explorer_tool(
    db: orm.Session, capella_version_ids: list[int]
) -> tools_models.DatabaseTool:
    model_explorer = tools_models.CreateTool(
        name="Capella model explorer",
        config=tools_models.ToolSessionConfiguration(
            environment={
                # MODEL_ENTRYPOINT AND ROUTE_PREFIX are added for compatibility with CME v0.2.X
                "MODEL_ENTRYPOINT": tools_models.ToolSessionEnvironment(
                    stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
                    value="{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}",
                ),
                "ROUTE_PREFIX": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
                "CME_MODEL": tools_models.ToolSessionEnvironment(
                    stage=tools_models.ToolSessionEnvironmentStage.BEFORE,
                    value={
                        "path": "{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}",
                        "diagram_cache": {
                            "path": "{CAPELLACOLLAB_SESSION_PROVISIONING[0][diagram_\
                            cache]}",
                            "password": "{CAPELLACOLLAB_SESSION_API_TOKEN}",
                            "username": "{CAPELLACOLLAB_SESSION_REQUESTER_USERNAME}",
                        },
                        "fallback_render_aird": "true",
                    },
                ),
                "CME_LOG_FILE": "/var/log/session/model-explorer.log",
                "CME_LIVE_MODE": "0",
                "CME_ROUTE_PREFIX": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
            },
            connection=tools_models.ToolSessionConnection(
                methods=[
                    tools_models.HTTPConnectionMethod(
                        name="Direct Browser connection",
                        sharing=tools_models.ToolSessionSharingConfiguration(
                            enabled=True
                        ),
                        ports=tools_models.HTTPPorts(http=8000, metrics=8000),
                        redirect_url=(
                            DEFAULT_REDIRECT_URL
                            + "{CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
                        ),
                    )
                ]
            ),
            monitoring=tools_models.SessionMonitoring(
                prometheus=tools_models.PrometheusConfiguration(
                    path="/metrics"
                )
            ),
            provisioning=tools_models.ToolModelProvisioning(
                directory="/models",
                max_number_of_models=1,
                required=False,
                provide_diagram_cache=True,
            ),
            persistent_workspaces=tools_models.PersistentWorkspaceSessionConfiguration(
                mounting_enabled=False,
            ),
        ),
    )
    model_explorer_database = tools_crud.create_tool(db, model_explorer)

    latest_release = tools_models.CreateToolVersion(
        name="Latest release",
        config=tools_models.ToolVersionConfiguration(
            sessions=tools_models.SessionToolConfiguration(
                persistent=tools_models.PersistentSessionToolConfiguration(
                    image=tools_models.PersistentSessionToolConfigurationImages(
                        regular=f"{config.docker.github_registry}/dsd-dbs/capella-model-explorer/model-explorer:latest",
                    ),
                ),
            ),
            compatible_versions=capella_version_ids,
        ),
    )

    latest_tag = tools_models.CreateToolVersion(
        name="Current development version",
        config=tools_models.ToolVersionConfiguration(
            sessions=tools_models.SessionToolConfiguration(
                persistent=tools_models.PersistentSessionToolConfiguration(
                    image=tools_models.PersistentSessionToolConfigurationImages(
                        regular=f"{config.docker.github_registry}/dsd-dbs/capella-model-explorer/model-explorer:master",
                    ),
                ),
            ),
            compatible_versions=capella_version_ids,
        ),
    )

    for version in (latest_release, latest_tag):
        tools_crud.create_version(
            db,
            model_explorer_database,
            version,
        )

    return model_explorer_database


def create_papyrus_tool(db: orm.Session) -> tools_models.DatabaseTool:
    papyrus = tools_models.CreateTool(
        name="Papyrus",
        integrations=tools_models.ToolIntegrations(
            t4c=False, pure_variants=False
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
                "JUPYTER_ALLOW_ORIGIN": DEFAULT_REDIRECT_URL,
            },
            connection=tools_models.ToolSessionConnection(
                methods=[
                    tools_models.HTTPConnectionMethod(
                        id="jupyter-direct",
                        name="Browser",
                        description="The only available connection method for Jupyter.",
                        ports=tools_models.HTTPPorts(http=8888, metrics=9118),
                        redirect_url=(
                            DEFAULT_REDIRECT_URL
                            + "{CAPELLACOLLAB_SESSIONS_BASE_PATH}/lab"
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
    _, capella_versions = create_capella_tool(db)
    create_capella_model_explorer_tool(
        db, [version.id for version in capella_versions]
    )

    if "localhost" in config.docker.sessions_registry:
        create_papyrus_tool(db)
        create_jupyter_tool(db)

    logger.info("Initialized tools")


def create_t4c_instance_and_repositories(db):
    tool = tools_crud.get_tool_by_name(db, "Capella")
    assert tool

    version = tools_crud.get_version_by_tool_id_version_name(
        db, tool.id, "7.0.0"
    )
    assert version

    _create_local_t4c_environment(db, version)
    _create_cluster_t4c_environment(db, version)
    logger.info("Initialized T4C instance and repositories")


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


def create_capellambse_test_models(
    db: orm.Session, project: project_models.DatabaseProject
):
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    for version in ["5.0.0", "5.2.0", "6.0.0"]:
        capella_model = toolmodels_crud.create_model(
            db=db,
            project=project,
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
                entrypoint=f"/tests/data/melodymodel/{version[:3].replace('.', '_')}/Melody Model Test.aird",
                revision="master",
                username="",
                password="",
            ),
        )


def initialize_coffee_machine_project(db: orm.Session):
    project = projects_crud.create_project(
        db=db,
        name="Coffee Machine",
        description="Contains the Capella Coffee Machine sample model",
        visibility=project_models.ProjectVisibility.INTERNAL,
    )
    create_coffee_machine_model(db, project)
    logger.info("Initialized project '%s'", project.name)


def create_coffee_machine_model(
    db: orm.Session, project: project_models.DatabaseProject
):
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    capella_model = toolmodels_crud.create_model(
        db=db,
        project=project,
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


def initialize_ife_project(db: orm.Session):
    project = projects_crud.create_project(
        db=db,
        name="In-Flight Entertainment",
        description="Contains the Capella In-Flight Entertainment System sample model",
        visibility=project_models.ProjectVisibility.INTERNAL,
    )
    create_ife_model(db, project)
    logger.info("Initialized project '%s'", project.name)


def create_ife_model(db: orm.Session, project: project_models.DatabaseProject):
    """Add the Capella In-Flight Entertainment project & model."""

    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    capella_model = toolmodels_crud.create_model(
        db=db,
        project=project,
        post_model=toolmodels_models.PostToolModel(
            name="In-Flight Entertainment",
            description=(
                "The Capella In-Flight Entertainment System sample model,"
                " with some modifications"
            ),
            tool_id=capella_tool.id,
        ),
        tool=capella_tool,
        version=tools_crud.get_version_by_tool_id_version_name(
            db, capella_tool.id, "7.0.0"
        ),
        nature=tools_crud.get_nature_by_name(db, capella_tool, "model"),
    )

    git_crud.add_git_model_to_capellamodel(
        db=db,
        capella_model=capella_model,
        post_git_model=git_models.PostGitModel(
            path="https://github.com/DSD-DBS/Capella-IFE-sample",
            entrypoint="In-Flight Entertainment System.aird",
            revision="master",
            username="",
            password="",
        ),
    )
