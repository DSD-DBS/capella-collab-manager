# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


# Standard library:
import typing as t

# 3rd party:
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as models_crud

# 1st party:
from capellacollab.extensions.modelsources.git.models import (
    DB_GitModel,
    NewGitSource,
    PostGitModel,
)


def get_gitmodels_of_capellamodels(
    db: Session, model_id: int
) -> t.List[DB_GitModel]:
    return db.query(DB_GitModel).filter(DB_GitModel.model_id == model_id).all()


def get_primary_gitmodel_of_capellamodels(db: Session, model_id: int):
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


def add_gitmodel_to_capellamodel(
    db: Session, capellamodel_id: int, model: PostGitModel
):
    if len(get_gitmodels_of_capellamodels(db, capellamodel_id)):
        primary = False
    else:
        primary = True

    # FIXME: Update the parameters according to the new structure
    model = DB_GitModel(
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
    db: Session, capellamodel_id: int, model_id: int
):
    db.query(DB_GitModel).filter(DB_GitModel.id == model_id).filter(
        DB_GitModel.model_id == capellamodel_id
    ).delete()
    db.commit()


def create(
    db: Session, project_slug: str, model_slug: str, source: NewGitSource
):

    model = models_crud.get_model_by_slug(db, project_slug, model_slug)
    new_source = DB_GitModel.from_new_git_source(model.id, source)
    db.add(new_source)
    db.commit()
    return new_source
