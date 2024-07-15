# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.users import models as users_models

from . import models


def get_workspaces_for_user(
    db: orm.Session, user: users_models.DatabaseUser
) -> abc.Sequence[models.DatabaseWorkspace]:
    return (
        db.execute(
            sa.select(models.DatabaseWorkspace).where(
                models.DatabaseWorkspace.user == user
            )
        )
        .scalars()
        .all()
    )


def get_workspace_by_id_and_user(
    db: orm.Session, user: users_models.DatabaseUser, workspace_id: int
) -> models.DatabaseWorkspace | None:
    return db.execute(
        sa.select(models.DatabaseWorkspace).where(
            models.DatabaseWorkspace.user == user,
            models.DatabaseWorkspace.id == workspace_id,
        )
    ).scalar_one_or_none()


def create_workspace(
    db: orm.Session,
    workspace: models.DatabaseWorkspace,
) -> models.DatabaseWorkspace:
    db.add(workspace)
    db.commit()
    return workspace


def delete_workspace(
    db: orm.Session, workspace: models.DatabaseWorkspace
) -> None:
    db.delete(workspace)
    db.commit()
