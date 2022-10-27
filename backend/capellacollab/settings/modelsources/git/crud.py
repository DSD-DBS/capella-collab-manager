# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.git.models import (
    DB_GitSettings,
    GitSettings,
)


def get_git_setting_by_id(db: Session, git_setting_id: int) -> DB_GitSettings:
    return (
        db.query(DB_GitSettings)
        .filter(DB_GitSettings.id == git_setting_id)
        .first()
    )


def get_git_settings(db: Session) -> t.List[DB_GitSettings]:
    return db.query(DB_GitSettings).all()


def create_git_setting(db: Session, body: GitSettings) -> DB_GitSettings:
    git_setting = DB_GitSettings(type=body.type, name=body.name, url=body.url)
    db.add(git_setting)

    db.commit()
    return git_setting


def update_git_setting(
    db: Session, git_setting: DB_GitSettings, update_git_setting: GitSettings
) -> DB_GitSettings:
    if update_git_setting.type:
        git_setting.type = update_git_setting.type
    if update_git_setting.name:
        git_setting.name = update_git_setting.name
    if update_git_setting.url:
        git_setting.url = update_git_setting.url

    db.commit()
    return git_setting


def delete_git_setting(db: Session, git_setting: DB_GitSettings) -> None:
    git_setting.delete()
    db.commit()
