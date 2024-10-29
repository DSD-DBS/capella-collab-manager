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

    database_tool = tools_crud.create_tool(db, tool)

    # pylint: disable=unused-argument
    def mock_get_existing_tool(*args, **kwargs) -> tools_models.DatabaseTool:
        return database_tool

    monkeypatch.setattr(
        tools_injectables, "get_existing_tool", mock_get_existing_tool
    )
    return database_tool


@pytest.fixture(name="tool_nature")
def fixture_tool_nature(
    db: orm.Session,
    monkeypatch: pytest.MonkeyPatch,
    tool: tools_models.DatabaseTool,
) -> tools_models.DatabaseNature:
    nature = tools_crud.create_nature(db, tool, "test")

    def get_existing_tool_nature(
        *args, **kwargs  # pylint: disable=unused-argument
    ) -> tools_models.DatabaseNature:
        return nature

    monkeypatch.setattr(
        tools_injectables,
        "get_existing_tool_nature",
        get_existing_tool_nature,
    )
    return nature


@pytest.fixture(name="capella_tool", params=["6.0.0"])
def fixture_capella_tool(db: orm.Session) -> tools_models.DatabaseTool:
    capella_tool = tools_crud.get_tool_by_name(db, "Capella")
    assert capella_tool

    return capella_tool


@pytest.fixture(name="jupyter_tool")
def fixture_jupyter_tool(db: orm.Session) -> tools_models.DatabaseTool:
    return database_migration.create_jupyter_tool(db)
