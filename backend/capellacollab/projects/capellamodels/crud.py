# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import HTTPException
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version

from .models import CapellaModelType, DB_CapellaModel, EditingMode, NewModel


def get_all(db: Session, project_slug: str) -> t.List[DB_CapellaModel]:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    return (
        db.query(DB_CapellaModel)
        .filter(DB_CapellaModel.project_name == project.name)
        .all()
    )


def get_slug(db: Session, project_slug: str, id: int) -> DB_CapellaModel:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    return db.query(DB_CapellaModel).filter(
        DB_CapellaModel.project_name == project.name,
        DB_CapellaModel.id == id,
    )


def create(
    db: Session, project_slug: str, new_model: NewModel
) -> DB_CapellaModel:
    project = (
        db.query(DatabaseProject)
        .filter(DatabaseProject.slug == project_slug)
        .first()
    )
    if not project:
        raise HTTPException(404, "Project not found.")
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    version = (
        db.query(Version).filter(Version.id == new_model.version_id).first()
    )
    model_type = db.query(Type).filter(Type.id == new_model.type_id).first()
    if not tool:
        raise HTTPException(404, "Tool not found.")
    if not version or version.tool_id != tool.id:
        raise HTTPException(404, f"Version not found for tool {tool.name}.")
    if not model_type or model_type.tool_id != tool.id:
        raise HTTPException(404, f"Type not found for tool {tool.name}.")

    model = DB_CapellaModel(
        name=new_model.name,
        description=new_model.description,
        editing_mode=EditingMode.GIT,
        model_type={
            "model": CapellaModelType.PROJECT,
            "library": CapellaModelType.LIBRARY,
        }[model_type.name],
        project_name=project.name,
    )
    db.add(model)
    db.commit()
    return model
