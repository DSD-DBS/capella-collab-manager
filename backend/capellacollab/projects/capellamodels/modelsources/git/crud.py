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


def make_git_model_primary(
    db: Session, capella_model_id: int, git_model_id: int
) -> DB_GitModel:
    primary_model = get_primary_gitmodel_of_capellamodels(db, capella_model_id)
    primary_model.primary = False

    patch_git_model = get_gitmodel_by_id(db, git_model_id)
    patch_git_model.primary = True

    db.commit()
    return patch_git_model


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
    model_id: int,
    model: PostGitModel,
) -> DB_GitModel:
    updated_model = get_gitmodel_by_id(db, model_id)

    updated_model.path = model.path
    updated_model.entrypoint = model.entrypoint
    updated_model.revision = model.revision

    if model.password:
        updated_model.username = model.username
        updated_model.password = model.password
    elif not model.username:
        updated_model.username = ""
        updated_model.password = ""

    db.commit()
    return updated_model
