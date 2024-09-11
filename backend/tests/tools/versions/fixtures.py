# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.tools import crud as tools_crud
from capellacollab.tools import injectables as tools_injectables
from capellacollab.tools import models as tools_models


@pytest.fixture(name="capella_tool_version", params=["6.0.0"])
def fixture_capella_tool_version(
    db: orm.Session,
    capella_tool: tools_models.DatabaseTool,
    request: pytest.FixtureRequest,
) -> tools_models.DatabaseVersion:
    capella_tool_version = tools_crud.get_version_by_tool_id_version_name(
        db, capella_tool.id, request.param
    )
    assert capella_tool_version

    return capella_tool_version


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
