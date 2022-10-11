# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.t4c import crud
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def load_instance(
    t4c_instance_id: int, db: Session = Depends(get_db)
) -> DatabaseT4CInstance:
    try:
        return crud.get_t4c_instance(t4c_instance_id, db)
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={
                "reason": f"The t4c instance with the id {t4c_instance_id} does not exist.",
            },
        )
