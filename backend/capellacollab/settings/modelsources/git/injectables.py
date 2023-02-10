# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.git import crud
from capellacollab.settings.modelsources.git.models import DatabaseGitInstance


def get_existing_git_instance(
    git_instance_id: int,
    db: Session = Depends(get_db),
) -> DatabaseGitInstance:
    if git_instance := crud.get_git_instance_by_id(db, git_instance_id):
        return git_instance

    raise HTTPException(
        status_code=400,
        detail={
            "err_code": "git_instance_not_found",
            "reason": f"The git setting ({git_instance_id}) does not exists",
        },
    )
