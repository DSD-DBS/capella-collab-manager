# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core import database

from . import crud, models


def get_existing_plugin(
    plugin_id: int, db: Session = Depends(database.get_db)
) -> models.DatabasePlugin:
    if plugin := crud.get_plugin_by_id(db, plugin_id):
        return plugin

    raise HTTPException(
        404,
        {
            "reason": f"The plugin with the id {plugin_id} was not found.",
        },
    )
