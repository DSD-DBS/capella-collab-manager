# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, models


def get_existing_git_instance(
    git_instance_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseGitInstance:
    if git_instance := crud.get_git_instance_by_id(db, git_instance_id):
        return git_instance

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "err_code": "git_instance_not_found",
            "reason": f"The git setting ({git_instance_id}) does not exists",
        },
    )
