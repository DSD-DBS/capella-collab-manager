# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from sqlalchemy.orm import Session

from t4cclient.extensions.modelsources.git.models import (
    DB_GitModel,
    PostGitModel,
    RepositoryGitModel,
)


def get_models_of_repository(
    db: Session, repository_name: str
) -> t.List[DB_GitModel]:
    return (
        db.query(DB_GitModel)
        .filter(DB_GitModel.repository_name == repository_name)
        .all()
    )


def get_primary_model_of_repository(db: Session, repository_name: str):
    return (
        db.query(DB_GitModel)
        .filter(DB_GitModel.repository_name == repository_name)
        .filter(DB_GitModel.primary == True)
        .first()
    )


def get_model_by_id(
    db: Session, repository_name: str, model_id: int
) -> DB_GitModel:
    return (
        db.query(DB_GitModel)
        .filter(DB_GitModel.repository_name == repository_name)
        .filter(DB_GitModel.id == model_id)
        .first()
    )


def make_model_primary(
    db: Session, repository_name: str, model_id: int
) -> DB_GitModel:
    primary_model = get_primary_model_of_repository(db, repository_name)
    if primary_model:
        primary_model.primary = False
        db.add(primary_model)

    new_primary_model = get_model_by_id(db, repository_name, model_id)
    new_primary_model.primary = True

    db.add(new_primary_model)
    db.commit()
    db.refresh(new_primary_model)
    return new_primary_model


def add_model_to_repository(
    db: Session, repository_name: str, model: PostGitModel
):
    if len(get_models_of_repository(db, repository_name)):
        primary = False
    else:
        primary = True

    model = DB_GitModel(
        repository_name=repository_name,
        **model.model.dict(),
        name=model.name,
        primary=primary,
        username=model.credentials.username,
        password=model.credentials.password,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def delete_model_from_repository(
    db: Session, repository_name: str, model_id: int
):
    db.query(DB_GitModel).filter(DB_GitModel.id == model_id).filter(
        DB_GitModel.repository_name == repository_name
    ).delete()
    db.commit()
