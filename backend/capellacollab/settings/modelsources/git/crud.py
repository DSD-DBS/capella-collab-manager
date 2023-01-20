# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.git.models import (
    DatabaseGitInstance,
    PostGitInstance,
)


def get_git_setting_by_id(
    db: Session, git_setting_id: int
) -> DatabaseGitInstance:
    return (
        db.query(DatabaseGitInstance)
        .filter(DatabaseGitInstance.id == git_setting_id)
        .first()
    )


def get_git_settings(db: Session) -> list[DatabaseGitInstance]:
    return db.query(DatabaseGitInstance).all()


def create_git_setting(
    db: Session, body: PostGitInstance
) -> DatabaseGitInstance:
    git_setting = DatabaseGitInstance(
        type=body.type, name=body.name, url=body.url
    )
    db.add(git_setting)

    db.commit()
    return git_setting


def update_git_setting(
    db: Session,
    git_setting: DatabaseGitInstance,
    post_git_setting: PostGitInstance,
) -> DatabaseGitInstance:
    if _type := post_git_setting.type:
        git_setting.type = _type
    if name := post_git_setting.name:
        git_setting.name = name
    if url := post_git_setting.url:
        git_setting.url = url

    db.commit()
    return git_setting


def delete_git_setting(db: Session, git_setting: DatabaseGitInstance):
    db.delete(git_setting)
    db.commit()
