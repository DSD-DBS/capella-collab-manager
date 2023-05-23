# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from collections.abc import Sequence

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from capellacollab.projects import models as projects_model
from capellacollab.projects.toolmodels.models import (
    DatabaseCapellaModel,
    PostCapellaModel,
)
from capellacollab.tools.models import Nature, Tool, Version

from .restrictions.models import DatabaseToolModelRestrictions


def get_models(db: Session) -> Sequence[DatabaseCapellaModel]:
    return db.execute(select(DatabaseCapellaModel)).scalars().all()


def get_models_by_version(
    db: Session, version_id: int
) -> Sequence[DatabaseCapellaModel]:
    return (
        db.execute(
            select(DatabaseCapellaModel).where(
                DatabaseCapellaModel.version_id == version_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_nature(
    db: Session, nature_id: int
) -> Sequence[DatabaseCapellaModel]:
    return (
        db.execute(
            select(DatabaseCapellaModel).where(
                DatabaseCapellaModel.nature_id == nature_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_tool(
    db: Session, tool_id: int
) -> Sequence[DatabaseCapellaModel]:
    return (
        db.execute(
            select(DatabaseCapellaModel).where(
                DatabaseCapellaModel.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def get_model_by_slugs(
    db: Session, project_slug: str, model_slug: str
) -> DatabaseCapellaModel | None:
    return db.execute(
        select(DatabaseCapellaModel)
        .options(joinedload(DatabaseCapellaModel.project))
        .where(
            DatabaseCapellaModel.project.has(
                projects_model.DatabaseProject.slug == project_slug
            )
        )
        .where(DatabaseCapellaModel.slug == model_slug)
    ).scalar_one_or_none()


def create_model(
    db: Session,
    project: projects_model.DatabaseProject,
    post_model: PostCapellaModel,
    tool: Tool,
    version: Version | None = None,
    nature: Nature | None = None,
) -> DatabaseCapellaModel:
    restrictions = DatabaseToolModelRestrictions()

    model = DatabaseCapellaModel(
        name=post_model.name,
        slug=slugify(post_model.name),
        description=post_model.description if post_model.description else "",
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
    db: Session, model: DatabaseCapellaModel, tool: Tool
) -> DatabaseCapellaModel:
    model.tool = tool
    db.commit()
    return model


def set_tool_details_for_model(
    db: Session, model: DatabaseCapellaModel, version: Version, nature: Nature
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


def delete_model(db: Session, model: DatabaseCapellaModel):
    db.delete(model)
    db.commit()
