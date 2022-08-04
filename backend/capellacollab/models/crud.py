# Standard library:
import typing as t

# 3rd party:
from sqlalchemy.orm import Session

# 1st party:
import capellacollab.projects.crud as projects_crud
from capellacollab.models.models import EmptyModel, Model, NewModel, ToolDetails
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


def get_all(db: Session, project_slug: str) -> t.List[Model]:
    project = (
        db.query(DatabaseProject).filter(DatabaseProject.slug == project_slug).first()
    )
    assert project is not None
    return db.query(Model).filter(Model.project_id == project.id).all()


def get_id(db: Session, id_: int) -> Model:
    return db.query(Model).filter(Model.id == id_).first()


def get_slug(db: Session, project_slug: str, slug: str) -> Model:
    project = projects_crud.get_slug(db, project_slug)
    model = (
        db.query(Model)
        .filter(
            Model.project_id == project.id,
            Model.slug == slug,
        )
        .first()
    )
    assert model is not None
    return model


def create_new(db: Session, project_slug: str, new_model: NewModel) -> Model:
    project = (
        db.query(DatabaseProject).filter(DatabaseProject.slug == project_slug).first()
    )
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    assert tool is not None
    model = Model.from_new_model(new_model, project)
    db.add(model)
    db.commit()
    return model


def create_empty(db: Session, project_slug: str, new_model: EmptyModel) -> Model:
    project = (
        db.query(DatabaseProject).filter(DatabaseProject.slug == project_slug).first()
    )
    tool = db.query(Tool).filter(Tool.id == new_model.tool_id).first()
    version = db.query(Version).filter(Version.id == new_model.version_id).first()
    model_type = db.query(Type).filter(Type.id == new_model.type_id).first()
    assert tool is not None and version is not None and model_type is not None
    assert version.tool_id == tool.id and model_type.tool_id == tool.id
    model = Model.from_empty_model(new_model, project)
    db.add(model)
    db.commit()
    return model


def set_tool_details(db: Session, model: Model, tool_details: ToolDetails):
    version = db.query(Version).filter(Version.id == tool_details.version_id).first()
    model_type = db.query(Type).filter(Type.id == tool_details.type_id).first()
    assert version is not None and model_type is not None
    model.version_id = version.id
    model.type_id = model_type.id
    db.add(model)
    db.commit()
    return model
