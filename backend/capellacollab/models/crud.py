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


def get_slug(db: Session, project_slug, slug) -> Model:
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    return db.query(Model).filter(
        Model.project_id == project.id,
        Model.slug == slug,
    )

def create(db: Session, project_slug, new_model: NewModel):
    project = db.query(DatabaseProject)\
        .filter(DatabaseProject.slug == project_slug).first()
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    version = db.query(Version).filter(Version.id == new_model.version_id).first()
    model_type = db.query(Type).filter(Type.id == new_model.type_id).first()
    assert version.tool == tool and model_type.tool == tool
    model = Model(
        name=new_model.name,
        slug=slugify(new_model.name),
        description=new_model.description,
        project_id=project.id,
        tool_id=tool.id, version_id=version.id, type_id=model_type.id,
    )
    db.add(model)
    db.commit()
    return model
