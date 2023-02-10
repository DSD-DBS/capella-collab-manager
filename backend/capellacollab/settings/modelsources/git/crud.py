# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.git.models import (
    DatabaseGitInstance,
    PostGitInstance,
)


def get_git_instance_by_id(
    db: Session, git_instance_id: int
) -> DatabaseGitInstance:
    return (
        db.query(DatabaseGitInstance)
        .filter(DatabaseGitInstance.id == git_instance_id)
        .first()
    )


def get_git_instances(db: Session) -> list[DatabaseGitInstance]:
    return db.query(DatabaseGitInstance).all()


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
    for key in post_git_instance.dict():
        if (value := getattr(post_git_instance, key)) is not None:
            setattr(git_instance, key, value)

    db.commit()
    return git_instance


def delete_git_instance(db: Session, git_instance: DatabaseGitInstance):
    db.delete(git_instance)
    db.commit()
