# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

from . import models


def get_git_instances(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseGitInstance]:
    return db.execute(sa.select(models.DatabaseGitInstance)).scalars().all()


def get_git_instance_by_id(
    db: orm.Session, git_instance_id: int
) -> models.DatabaseGitInstance | None:
    return db.execute(
        sa.select(models.DatabaseGitInstance).where(
            models.DatabaseGitInstance.id == git_instance_id
        )
    ).scalar_one_or_none()


def create_git_instance(
    db: orm.Session, body: models.PostGitInstance
) -> models.DatabaseGitInstance:
    git_instance = models.DatabaseGitInstance(
        type=body.type, name=body.name, url=body.url, api_url=body.api_url
    )

    db.add(git_instance)
    db.commit()
    return git_instance


def update_git_instance(
    db: orm.Session,
    git_instance: models.DatabaseGitInstance,
    post_git_instance: models.PostGitInstance,
) -> models.DatabaseGitInstance:
    database.patch_database_with_pydantic_object(
        git_instance, post_git_instance
    )

    db.commit()
    return git_instance


def delete_git_instance(
    db: orm.Session, git_instance: models.DatabaseGitInstance
) -> None:
    db.delete(git_instance)
    db.commit()
