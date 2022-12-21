# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

import capellacollab.projects.crud as projects_crud
from capellacollab.projects.models import DatabaseProject
from capellacollab.projects.toolmodels.models import (
    DatabaseCapellaModel,
    PostCapellaModel,
)
from capellacollab.tools.models import Nature, Tool, Version

from .restrictions.models import DatabaseToolModelRestrictions


def get_all_models(db: Session) -> list[DatabaseCapellaModel]:
    return db.execute(select(DatabaseCapellaModel)).scalars().all()


def get_all_models_in_project(
    db: Session, project: DatabaseProject
) -> list[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.project_id == project.id)
        .all()
    )


def get_models_by_version(
    version_id: int, db: Session
) -> list[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.version_id == version_id)
        .all()
    )


def get_models_by_nature(
    nature_id: int, db: Session
) -> list[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.nature_id == nature_id)
        .all()
    )


def get_models_by_tool(
    tool_id: int, db: Session
) -> list[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.tool_id == tool_id)
        .all()
    )


def get_model_by_id(db: Session, id_: int) -> DatabaseCapellaModel:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.id == id_)
        .first()
    )


def get_model_by_slug(
    db: Session, project_slug: str, model_slug: str
) -> DatabaseCapellaModel:
    project = projects_crud.get_project_by_slug(db, project_slug)
    model = (
        db.query(DatabaseCapellaModel)
        .filter(
            DatabaseCapellaModel.project_id == project.id,
            DatabaseCapellaModel.slug == model_slug,
        )
        .first()
    )
    return model


def create_new_model(
    db: Session,
    project: DatabaseProject,
    new_model: PostCapellaModel,
    tool: Tool,
    version: Version | None = None,
    nature: Nature | None = None,
) -> DatabaseCapellaModel:
    restrictions = DatabaseToolModelRestrictions()

    model = DatabaseCapellaModel(
        name=new_model.name,
        slug=slugify(new_model.name),
        description=new_model.description,
        project=project,
        tool=tool,
        version=version,
        nature=nature,
        restrictions=restrictions,
    )
    db.add(model)
    db.commit()
    return model


def set_tool_for_model(
    db: Session,
    model: DatabaseCapellaModel,
    tool: Tool,
) -> DatabaseCapellaModel:
    model.tool = tool
    db.commit()
    return model


def set_tool_details_for_model(
    db: Session,
    model: DatabaseCapellaModel,
    version: Version,
    nature: Nature,
) -> DatabaseCapellaModel:
    model.version = version
    model.nature = nature
    db.commit()
    return model


def update_model(
    db: Session,
    model: DatabaseCapellaModel,
    description: str | None,
    version: Version,
    nature: Nature,
) -> DatabaseCapellaModel:
    model.version = version
    model.nature = nature
    if description:
        model.description = description
    db.commit()
    return model


def delete_model(
    db: Session,
    model: DatabaseCapellaModel,
):
    db.delete(model)
    db.commit()
