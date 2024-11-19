# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pytest
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.provisioning import (
    crud as provisioning_crud,
)
from capellacollab.projects.toolmodels.provisioning import (
    models as provisioning_models,
)
from capellacollab.users import models as users_models


@pytest.fixture(name="provisioning")
def fixture_provisioning(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    return provisioning_crud.create_model_provisioning(
        db,
        provisioning_models.DatabaseModelProvisioning(
            user=user,
            tool_model=capella_model,
            revision="main",
            commit_hash="db45166576e7f1e7fec3256e8657ba431f9b5b77",
            provisioned_at=datetime.datetime.now(),
            session=None,
        ),
    )
