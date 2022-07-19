import typing as t

from h11 import Data
from slugify import slugify
from sqlalchemy import insert
from sqlalchemy.orm import Session

from .models import CapellaModelType, DB_CapellaModel, EditingMode, NewModel
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


def get_all(db: Session, project_slug: str) -> t.List[DB_CapellaModel]:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    return db.query(DB_CapellaModel)\
        .filter(DB_CapellaModel.project_name == project.name).all()


def get_slug(db: Session, project_slug: str, id: int) -> DB_CapellaModel:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    return db.query(DB_CapellaModel).filter(
        DB_CapellaModel.project_name == project.name,
        DB_CapellaModel.id == id,
    )

def create(db: Session, project_slug, new_model: NewModel) -> DB_CapellaModel:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    version = db.query(Version).filter(Version.id == new_model.version_id).first()
    model_type = db.query(Type).filter(Type.id == new_model.type_id).first()
    assert version.tool == tool and model_type.tool == tool
    model = DB_CapellaModel(
        name=new_model.name,
        description=new_model.description,
        editing_mode=EditingMode.GIT,
        model_type={'model': CapellaModelType.PROJECT, 'library': CapellaModelType.LIBRARY}[model_type.name],
        project_name=project.name,
    )
    db.add(model)
    db.commit()
    return model
