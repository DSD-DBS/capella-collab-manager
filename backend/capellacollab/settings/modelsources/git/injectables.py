# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.settings.modelsources.git.crud as crud
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git.models import DB_GitSettings


def get_existng_git_setting(
    git_setting_id: int,
    db: Session = Depends(get_db),
) -> DB_GitSettings:
    if git_setting := crud.get_git_setting_by_id(db, git_setting_id):
        return git_setting

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "git_setting_not_found",
            "reason": f"The git setting ({git_setting_id}) does not exists",
        },
    )
