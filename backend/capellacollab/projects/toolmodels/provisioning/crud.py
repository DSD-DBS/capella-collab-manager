# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.users import models as users_models

from . import models


def create_model_provisioning(
    db: orm.Session, model: models.DatabaseModelProvisioning
) -> models.DatabaseModelProvisioning:
    db.add(model)
    db.commit()
    return model


def get_model_provisioning(
    db: orm.Session,
    tool_model: toolmodels_models.DatabaseToolModel,
    user: users_models.DatabaseUser,
) -> models.DatabaseModelProvisioning | None:
    return db.execute(
        sa.select(models.DatabaseModelProvisioning)
        .where(models.DatabaseModelProvisioning.tool_model == tool_model)
        .where(models.DatabaseModelProvisioning.user == user)
    ).scalar_one_or_none()


def delete_model_provisioning(
    db: orm.Session, provisioning: models.DatabaseModelProvisioning
):
    db.delete(provisioning)
    db.commit()
