# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


# Standard library:
import typing as t

from fastapi import HTTPException

# 3rd party:
from sqlalchemy.orm import Session

# 1st party:
import capellacollab.projects.crud as projects_crud
from capellacollab.projects.capellamodels.models import (
    Model,
    NewModel,
    ToolDetails,
)
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


def get_all_models(db: Session, project_slug: str) -> t.List[Model]:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    return db.query(Model).filter(Model.project_id == project.id).all()


def get_model_by_id(db: Session, id_: int) -> Model:
    return db.query(Model).filter(Model.id == id_).first()


def get_model_by_slug(db: Session, project_slug: str, slug: str) -> Model:
    project = projects_crud.get_project_by_slug(db, project_slug)
    model = (
        db.query(Model)
        .filter(
            Model.project_id == project.id,
            Model.slug == slug,
        )
        .first()
    )
    return model


def create_new_model(
    db: Session, project_slug: str, new_model: NewModel
) -> Model:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    if not tool:
        raise HTTPException(
            404,
            {"reason": f"The tool with id {new_model.tool_id} was not found."},
        )
    model = Model.from_new_model(new_model, project)
    db.add(model)
    db.commit()
    return model


def set_tool_details_for_model(
    db: Session, model: Model, tool_details: ToolDetails
):
    version = (
        db.query(Version).filter(Version.id == tool_details.version_id).first()
    )
    model_type = db.query(Type).filter(Type.id == tool_details.type_id).first()
    if not version:
        raise HTTPException(
            404,
            {
                "reason": f"The version with id {model.verison_id} was not found."
            },
        )
    if not model_type:
        raise HTTPException(
            404, {"reason": f"The type with id {model.type_id} was not found."}
        )
    model.version_id = version.id
    model.type_id = model_type.id
    db.add(model)
    db.commit()
    return model
