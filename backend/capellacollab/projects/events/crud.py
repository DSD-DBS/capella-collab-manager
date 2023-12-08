# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi_pagination.ext.sqlalchemy
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.events import models as events_models
from capellacollab.projects import models as projects_models


def get_events_per_project_paginated(
    db: orm.Session, project: projects_models.DatabaseProject
) -> fastapi_pagination.Page[events_models.DatabaseUserHistoryEvent]:
    return fastapi_pagination.ext.sqlalchemy.paginate(
        db,
        sa.select(events_models.DatabaseUserHistoryEvent)
        .where(events_models.DatabaseUserHistoryEvent.project == project)
        .order_by(events_models.DatabaseUserHistoryEvent.id.desc()),
    )
