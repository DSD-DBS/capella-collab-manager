# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects.toolmodels import models as toolsmodels_models
from capellacollab.projects.toolmodels.modelsources.git import models


def get_git_model_by_id(
    db: orm.Session, git_model_id: int
) -> models.DatabaseGitModel | None:
    return db.execute(
        sa.select(models.DatabaseGitModel).where(
            models.DatabaseGitModel.id == git_model_id
        )
    ).scalar_one_or_none()


def get_primary_git_model_of_capellamodel(
    db: orm.Session, model_id: int
) -> models.DatabaseGitModel | None:
    return db.execute(
        sa.select(models.DatabaseGitModel)
        .where(models.DatabaseGitModel.model_id == model_id)
        .where(models.DatabaseGitModel.primary)
    ).scalar_one_or_none()


def add_git_model_to_capellamodel(
    db: orm.Session,
    capella_model: toolsmodels_models.DatabaseToolModel,
    post_git_model: models.PostGitModel,
) -> models.DatabaseGitModel:
    primary = not get_primary_git_model_of_capellamodel(db, capella_model.id)

    git_model = models.DatabaseGitModel.from_post_git_model(
        capella_model, primary, post_git_model
    )

    db.add(git_model)
    db.commit()
    return git_model


def make_git_model_primary(
    db: orm.Session, git_model: models.DatabaseGitModel
) -> models.DatabaseGitModel:
    if primary_model := get_primary_git_model_of_capellamodel(
        db, git_model.model_id
    ):
        primary_model.primary = False

    git_model.primary = True

    db.commit()
    return git_model


def update_git_model(
    db: orm.Session,
    git_model: models.DatabaseGitModel,
    put_model: models.PutGitModel,
) -> models.DatabaseGitModel:
    git_model.path = put_model.path
    git_model.entrypoint = put_model.entrypoint
    git_model.revision = put_model.revision
    git_model.repository_id = None

    if put_model.password:
        git_model.username = put_model.username
        git_model.password = put_model.password
    elif not put_model.username:
        git_model.username = ""
        git_model.password = ""

    if put_model.primary and not git_model.primary:
        git_model = make_git_model_primary(db, git_model)

    db.commit()
    return git_model


def update_git_model_repository_id(
    db: orm.Session, git_model: models.DatabaseGitModel, repository_id: str
) -> models.DatabaseGitModel:
    git_model.repository_id = repository_id

    db.commit()
    return git_model


def delete_git_model(db: orm.Session, git_model: models.DatabaseGitModel):
    db.delete(git_model)
    db.commit()
