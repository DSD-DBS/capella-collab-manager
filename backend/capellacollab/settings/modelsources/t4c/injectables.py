# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.t4c import crud
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance


def get_existing_instance(
    t4c_instance_id: int, db: Session = Depends(get_db)
) -> DatabaseT4CInstance:
    if t4c_instance := crud.get_t4c_instance_by_id(db, t4c_instance_id):
        return t4c_instance

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The t4c instance with the id {t4c_instance_id} does not exist.",
        },
    )
