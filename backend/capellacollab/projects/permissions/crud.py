# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.users.tokens import models as tokens_models

from . import models


def create_project_token(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    token: tokens_models.DatabaseUserToken,
    scope: models.ProjectUserScopes,
) -> models.DatabaseProjectPATAssociation:
    model = models.DatabaseProjectPATAssociation(
        token=token, project=project, scope=scope
    )
    db.add(model)
    db.commit()
    return model


def get_project_token(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    token: tokens_models.DatabaseUserToken,
) -> models.DatabaseProjectPATAssociation | None:
    return db.execute(
        sa.select(models.DatabaseProjectPATAssociation)
        .where(models.DatabaseProjectPATAssociation.project == project)
        .where(models.DatabaseProjectPATAssociation.token == token)
    ).scalar_one_or_none()
