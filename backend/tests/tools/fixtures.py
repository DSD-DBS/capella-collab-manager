# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.core.database import migration as database_migration
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models


@pytest.fixture(name="tool")
def fixture_tool(
    monkeypatch: pytest.MonkeyPatch, db: orm.Session
) -> tools_models.DatabaseTool:
    tool = tools_models.CreateTool(
        name="test",
        integrations=tools_models.ToolIntegrations(),
        config=database_migration.get_eclipse_session_configuration(),
    )

    tool = tools_crud.create_tool(db, tool)

    def mock_get_existing_tool(*args, **kwargs) -> tools_models.DatabaseTool:
        return tool

    monkeypatch.setattr(
        tools_injectables, "get_existing_tool", mock_get_existing_tool
    )
    return tool


@pytest.fixture(name="tool_version")
def fixture_tool_version(
    db: orm.Session,
    monkeypatch: pytest.MonkeyPatch,
    tool: tools_models.DatabaseTool,
) -> tools_models.DatabaseVersion:
    tool_version = tools_models.CreateToolVersion(
        name="test", config=tools_models.ToolVersionConfiguration()
    )

    version = tools_crud.create_version(db, tool, tool_version)

    def get_existing_tool_version(
        *args, **kwargs
    ) -> tools_models.DatabaseVersion:
        return version

    monkeypatch.setattr(
        tools_injectables,
        "get_existing_tool_version",
        get_existing_tool_version,
    )
    return version


@pytest.fixture(name="tool_nature")
def fixture_tool_nature(
    db: orm.Session,
    monkeypatch: pytest.MonkeyPatch,
    tool: tools_models.DatabaseTool,
) -> tools_models.DatabaseNature:
    nature = tools_crud.create_nature(db, tool, "test")

    def get_existing_tool_nature(
        *args, **kwargs
    ) -> tools_models.DatabaseNature:
        return nature

    monkeypatch.setattr(
        tools_injectables,
        "get_existing_tool_nature",
        get_existing_tool_nature,
    )
    return nature


@pytest.fixture(name="capella_tool_version", params=["6.0.0"])
def fixture_capella_tool_version(
    db: orm.Session,
    request: pytest.FixtureRequest,
) -> tools_models.DatabaseVersion:
    return tools_crud.get_version_by_tool_id_version_name(
        db, tools_crud.get_tool_by_name(db, "Capella").id, request.param
    )


@pytest.fixture(name="jupyter_tool")
def fixture_jupyter_tool(db: orm.Session) -> tools_models.DatabaseTool:
    return database_migration.create_jupyter_tool(db)
