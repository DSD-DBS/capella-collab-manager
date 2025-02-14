# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, exceptions, models


def get_existing_git_instance(
    git_instance_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseGitInstance:
    if git_instance := crud.get_git_instance_by_id(db, git_instance_id):
        return git_instance

    raise exceptions.GitServerNotFound(git_instance_id)
