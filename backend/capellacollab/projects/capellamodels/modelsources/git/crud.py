# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as models_crud
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DB_GitModel,
    PostGitModel,
)


def get_gitmodels_of_capellamodels(
    db: Session, model_id: int
) -> t.List[DB_GitModel]:
    return db.query(DB_GitModel).filter(DB_GitModel.model_id == model_id).all()


def get_primary_gitmodel_of_capellamodels(
    db: Session, model_id: int
) -> DB_GitModel:
    return (
        db.query(DB_GitModel)
        .filter(DB_GitModel.model_id == model_id)
        .filter(DB_GitModel.primary)
        .first()
    )


def get_gitmodel_by_id(db: Session, id: int) -> DB_GitModel:
    return db.query(DB_GitModel).filter(DB_GitModel.id == id).first()


def make_gitmodel_primary(db: Session, id: int) -> DB_GitModel:
    primary_model = get_primary_gitmodel_of_capellamodels(db, id)
    if primary_model:
        primary_model.primary = False
        db.add(primary_model)

    new_primary_model = get_gitmodel_by_id(db, id)
    new_primary_model.primary = True

    db.add(new_primary_model)
    db.commit()
    db.refresh(new_primary_model)
    return new_primary_model


def delete_model_from_repository(
    db: Session, capellamodel_id: int, model_id: int
):
    db.query(DB_GitModel).filter(DB_GitModel.id == model_id).filter(
        DB_GitModel.model_id == capellamodel_id
    ).delete()
    db.commit()


def add_gitmodel_to_capellamodel(
    db: Session, project_slug: str, model_slug: str, source: PostGitModel
) -> DB_GitModel:
    model = models_crud.get_model_by_slug(db, project_slug, model_slug)

    if len(get_gitmodels_of_capellamodels(db, model.id)):
        primary = False
    else:
        primary = True
    new_model = DB_GitModel.from_post_git_model(model.id, primary, source)
    db.add(new_model)
    db.commit()
    db.refresh(model)
    return new_model


def update_git_model(
    db: Session,
    id: int,
    project_slug: str,
    model_slug: str,
    source: PostGitModel,
) -> DB_GitModel:
    model = get_gitmodel_by_id(db, id)

    model.path = source.path
    model.entrypoint = source.entrypoint
    model.revision = source.revision

    if source.password:
        model.username = source.username
        model.password = source.password
    elif not source.username:
        model.username = ""
        model.password = ""
    db.commit()
    return model
