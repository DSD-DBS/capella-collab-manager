# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as models_crud
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DB_GitModel,
    PatchGitModel,
    PostGitModel,
)


def get_gitmodels_of_capellamodels(
    db: Session, model_id: int
) -> t.List[DB_GitModel]:
    return db.query(DB_GitModel).filter(DB_GitModel.model_id == model_id).all()


def get_primary_gitmodel_of_capellamodel(
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
    primary_model = get_primary_gitmodel_of_capellamodel(db, capella_model_id)
    primary_model.primary = False

    patch_git_model = get_gitmodel_by_id(db, git_model_id)
    patch_git_model.primary = True

    db.commit()
    return patch_git_model


def add_gitmodel_to_capellamodel(
    db: Session,
    capella_model: DatabaseCapellaModel,
    post_git_model: PostGitModel,
) -> DB_GitModel:
    if len(get_gitmodels_of_capellamodels(db, capella_model.id)):
        primary = False
    else:
        primary = True
    new_model = DB_GitModel.from_post_git_model(
        capella_model.id, primary, post_git_model
    )
    db.add(new_model)
    db.commit()

    return new_model


def update_git_model(
    db: Session,
    db_capella_model: DatabaseCapellaModel,
    db_model: DB_GitModel,
    patch_model: PatchGitModel,
) -> DB_GitModel:
    db_model.path = patch_model.path
    db_model.entrypoint = patch_model.entrypoint
    db_model.revision = patch_model.revision

    if patch_model.password:
        db_model.username = patch_model.username
        db_model.password = patch_model.password
    elif not patch_model.username:
        db_model.username = ""
        db_model.password = ""

    if patch_model.primary and not db_model.primary:
        db_model = make_git_model_primary(db, db_capella_model.id, db_model.id)

    db.commit()
    return db_model
