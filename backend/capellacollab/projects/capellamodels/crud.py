# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from slugify import slugify
from sqlalchemy.orm import Session

import capellacollab.projects.crud as projects_crud
from capellacollab.projects.capellamodels.models import (
    CapellaModel,
    DatabaseCapellaModel,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


def get_all_models_in_project(
    db: Session, project_slug: str
) -> t.List[DatabaseCapellaModel]:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.project_id == project.id)
        .all()
    )


def get_models_by_version(
    version_id: int, db: Session
) -> t.List[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.version_id == version_id)
        .all()
    )


def get_models_by_type(
    type_id: int, db: Session
) -> t.List[DatabaseCapellaModel]:
    return (
        db.query(DatabaseCapellaModel)
        .filter(DatabaseCapellaModel.type_id == type_id)
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
    db: Session, project: DatabaseProject, new_model: CapellaModel, tool: Tool
) -> DatabaseCapellaModel:
    model = DatabaseCapellaModel(
        name=new_model.name,
        slug=slugify(new_model.name),
        description=new_model.description,
        project=project,
        tool=tool,
    )
    db.add(model)
    db.commit()
    return model


def set_tool_details_for_model(
    db: Session,
    model: DatabaseCapellaModel,
    version: Version,
    model_type: Type,
):
    model.version = version
    model.tool_type = model_type
    db.add(model)
    db.commit()
    return model
