# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.git.models import (
    DB_GitSettings,
    GitSettings,
    GitSettingsGitGetResponse,
)


def get_git_settings(db: Session, id: int) -> GitSettingsGitGetResponse:
    return db.query(DB_GitSettings).filter(DB_GitSettings.id == id).first()


def get_all_git_settings(db: Session) -> t.List[GitSettingsGitGetResponse]:
    return db.query(DB_GitSettings).all()


def create_git_settings(db: Session, body: GitSettings):
    git_settings = DB_GitSettings(type=body.type, name=body.name, url=body.url)
    db.add(git_settings)
    db.commit()
    db.refresh(git_settings)
    return git_settings


def update_git_settings(db: Session, id: int, body: GitSettings):
    git_settings = get_git_settings(db, id)
    git_settings.type = body.type if body.type else git_settings.type
    git_settings.name = body.name if body.name else git_settings.name
    git_settings.url = body.url if body.url else git_settings.url
    db.commit()
    return git_settings


def delete_git_settings(db: Session, id: int) -> None:
    db.query(DB_GitSettings).filter(DB_GitSettings.id == id).delete()
    db.commit()
