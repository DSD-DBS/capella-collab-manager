import typing as t

from h11 import Data
from slugify import slugify
from sqlalchemy import insert
from sqlalchemy.orm import Session

from capellacollab.models.models import Model, NewModel
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


def get_all(db: Session, project_slug: str) -> t.List[Model]:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    return db.query(Model)\
        .filter(Model.project_id == project.id).all()


def get_id(db: Session, id: int) -> Model:
    return db.query(Model)\
        .filter(Model.id == id).first()


def get_slug(db: Session, project_slug: str, slug: str) -> Model:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    return db.query(Model).filter(
        Model.project_id == project.id,
        Model.slug == slug,
    ).first()

def create(db: Session, project_slug, new_model: NewModel) -> Model:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    version = db.query(Version).filter(Version.id == new_model.version_id).first()
    model_type = db.query(Type).filter(Type.id == new_model.type_id).first()
    assert tool is not None and version is not None and model_type is not None
    assert version.tool_id == tool.id and model_type.tool_id == tool.id
    model = Model.from_new_model(new_model, project)
    db.add(model)
    db.commit()
    return model
