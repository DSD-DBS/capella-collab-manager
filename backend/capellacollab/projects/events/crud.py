# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi_pagination.ext.sqlalchemy
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.users.events import models as users_events_models


def get_events_per_project_paginated(
    db: orm.Session, project: projects_models.DatabaseProject
) -> fastapi_pagination.Page[users_events_models.DatabaseUserHistoryEvent]:
    return fastapi_pagination.ext.sqlalchemy.paginate(
        db,
        sa.select(users_events_models.DatabaseUserHistoryEvent)
        .where(users_events_models.DatabaseUserHistoryEvent.project == project)
        .order_by(users_events_models.DatabaseUserHistoryEvent.id.desc()),
    )
