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


def create_git_instance(
    db: Session, body: PostGitInstance
) -> DatabaseGitInstance:
    git_instance = DatabaseGitInstance(
        type=body.type, name=body.name, url=body.url, api_url=body.api_url
    )
    db.add(git_instance)

    db.commit()
    return git_instance


def update_git_setting(
    db: Session,
    git_setting: DatabaseGitInstance,
    post_git_setting: PostGitInstance,
) -> DatabaseGitInstance:
    for key in post_git_setting.dict():
        if (value := getattr(post_git_setting, key)) is not None:
            setattr(git_setting, key, value)

    db.commit()
    return git_setting


def delete_git_setting(db: Session, git_setting: DatabaseGitInstance):
    db.delete(git_setting)
    db.commit()
