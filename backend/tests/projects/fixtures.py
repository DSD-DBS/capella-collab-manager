# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import pytest
from sqlalchemy import orm

from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.volumes import crud as projects_volumes_crud
from capellacollab.projects.volumes import models as projects_volumes_models


@pytest.fixture(name="project")
def fixture_project(db: orm.Session) -> projects_models.DatabaseProject:
    return projects_crud.create_project(db, str(uuid.uuid1()))


@pytest.fixture(name="training_project")
def fixture_training_project(
    db: orm.Session,
) -> projects_models.DatabaseProject:
    return projects_crud.create_project(
        db, str(uuid.uuid1()), type=projects_models.ProjectType.TRAINING
    )


@pytest.fixture(name="project_volume")
def fixture_project_volume(
    db: orm.Session, project: projects_models.DatabaseProject
) -> projects_volumes_models.DatabaseProjectVolume:
    return projects_volumes_crud.create_project_volume(
        db, project, "shared-workspace-test", "2Gi"
    )
