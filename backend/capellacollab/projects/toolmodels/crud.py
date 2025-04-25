# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import slugify
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.tools import models as tools_models

from . import models
from .restrictions import models as restrictions_models


def get_models(db: orm.Session) -> abc.Sequence[models.DatabaseToolModel]:
    return db.execute(sa.select(models.DatabaseToolModel)).scalars().all()


def get_models_by_version(
    db: orm.Session, version_id: int
) -> abc.Sequence[models.DatabaseToolModel]:
    return (
        db.execute(
            sa.select(models.DatabaseToolModel).where(
                models.DatabaseToolModel.version_id == version_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_nature(
    db: orm.Session, nature_id: int
) -> abc.Sequence[models.DatabaseToolModel]:
    return (
        db.execute(
            sa.select(models.DatabaseToolModel).where(
                models.DatabaseToolModel.nature_id == nature_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_tool(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.DatabaseToolModel]:
    return (
        db.execute(
            sa.select(models.DatabaseToolModel).where(
                models.DatabaseToolModel.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def get_model_by_slugs(
    db: orm.Session, project_slug: str, model_slug: str
) -> models.DatabaseToolModel | None:
    return db.execute(
        sa.select(models.DatabaseToolModel)
        .options(orm.joinedload(models.DatabaseToolModel.project))
        .where(
            models.DatabaseToolModel.project.has(
                projects_models.DatabaseProject.slug == project_slug
            )
        )
        .where(models.DatabaseToolModel.slug == model_slug)
    ).scalar_one_or_none()


def create_model(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    post_model: models.PostToolModel,
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion | None = None,
    nature: tools_models.DatabaseNature | None = None,
    display_order: int | None = None,
) -> models.DatabaseToolModel:
    model = models.DatabaseToolModel(
        name=post_model.name,
        slug=slugify.slugify(post_model.name),
        description=post_model.description if post_model.description else "",
        project=project,
        tool=tool,
        version=version,
        nature=nature,
        display_order=display_order,
    )

    restrictions = restrictions_models.DatabaseToolModelRestrictions(
        model=model
    )
    db.add(restrictions)
    db.add(model)
    db.commit()
    return model


def set_tool_for_model(
    db: orm.Session,
    model: models.DatabaseToolModel,
    tool: tools_models.DatabaseTool,
) -> models.DatabaseToolModel:
    model.tool = tool
    db.commit()
    return model


def set_tool_details_for_model(
    db: orm.Session,
    model: models.DatabaseToolModel,
    version: tools_models.DatabaseVersion,
    nature: tools_models.DatabaseNature,
) -> models.DatabaseToolModel:
    model.version = version
    model.nature = nature
    db.commit()
    return model


def update_model(
    db: orm.Session,
    model: models.DatabaseToolModel,
    description: str | None,
    name: str | None,
    version: tools_models.DatabaseVersion | None,
    nature: tools_models.DatabaseNature | None,
    project: projects_models.DatabaseProject,
    display_order: int | None,
) -> models.DatabaseToolModel:
    model.version = version
    model.nature = nature
    model.project = project
    if description:
        model.description = description
    if name:
        model.name = name
    if display_order:
        model.display_order = display_order
    db.commit()
    return model


def delete_model(db: orm.Session, model: models.DatabaseToolModel):
    db.delete(model)
    db.commit()
