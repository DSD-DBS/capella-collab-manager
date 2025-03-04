# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.settings.modelsources.git.crud as git_crud
import capellacollab.settings.modelsources.git.models as git_models


@pytest.fixture(name="git_instance")
def fixture_git_instance(
    db: orm.Session, git_type: git_models.GitType
) -> git_models.DatabaseGitInstance:
    git_instance = git_models.PostGitInstance(
        name="test",
        url="https://example.com/test/project",
        api_url="https://example.com/api/v4",
        type=git_type,
    )
    return git_crud.create_git_instance(db, git_instance)
