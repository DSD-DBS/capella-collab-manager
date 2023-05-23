# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object
from capellacollab.settings.modelsources.git.models import (
    DatabaseGitInstance,
    PostGitInstance,
)


def get_git_instances(db: Session) -> Sequence[DatabaseGitInstance]:
    return db.execute(select(DatabaseGitInstance)).scalars().all()


def get_git_instance_by_id(
    db: Session, git_instance_id: int
) -> DatabaseGitInstance | None:
    return db.execute(
        select(DatabaseGitInstance).where(
            DatabaseGitInstance.id == git_instance_id
        )
    ).scalar_one_or_none()


def create_git_instance(
    db: Session, body: PostGitInstance
) -> DatabaseGitInstance:
    git_instance = DatabaseGitInstance(
        type=body.type, name=body.name, url=body.url, api_url=body.api_url
    )

    db.add(git_instance)
    db.commit()
    return git_instance


def update_git_instance(
    db: Session,
    git_instance: DatabaseGitInstance,
    post_git_instance: PostGitInstance,
) -> DatabaseGitInstance:
    patch_database_with_pydantic_object(git_instance, post_git_instance)

    db.commit()
    return git_instance


def delete_git_instance(
    db: Session, git_instance: DatabaseGitInstance
) -> None:
    db.delete(git_instance)
    db.commit()
