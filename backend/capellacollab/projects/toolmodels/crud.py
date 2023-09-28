# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import slugify
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_model
from capellacollab.tools import models as tools_models

from . import models
from .restrictions import models as restrictions_models


def get_models(db: orm.Session) -> abc.Sequence[models.DatabaseCapellaModel]:
    return db.execute(sa.select(models.DatabaseCapellaModel)).scalars().all()


def get_models_by_version(
    db: orm.Session, version_id: int
) -> abc.Sequence[models.DatabaseCapellaModel]:
    return (
        db.execute(
            sa.select(models.DatabaseCapellaModel).where(
                models.DatabaseCapellaModel.version_id == version_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_nature(
    db: orm.Session, nature_id: int
) -> abc.Sequence[models.DatabaseCapellaModel]:
    return (
        db.execute(
            sa.select(models.DatabaseCapellaModel).where(
                models.DatabaseCapellaModel.nature_id == nature_id
            )
        )
        .scalars()
        .all()
    )


def get_models_by_tool(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.DatabaseCapellaModel]:
    return (
        db.execute(
            sa.select(models.DatabaseCapellaModel).where(
                models.DatabaseCapellaModel.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def get_model_by_slugs(
    db: orm.Session, project_slug: str, model_slug: str
) -> models.DatabaseCapellaModel | None:
    return db.execute(
        sa.select(models.DatabaseCapellaModel)
        .options(orm.joinedload(models.DatabaseCapellaModel.project))
        .where(
            models.DatabaseCapellaModel.project.has(
                projects_model.DatabaseProject.slug == project_slug
            )
        )
        .where(models.DatabaseCapellaModel.slug == model_slug)
    ).scalar_one_or_none()


def create_model(
    db: orm.Session,
    project: projects_model.DatabaseProject,
    post_model: models.PostCapellaModel,
    tool: tools_models.DatabaseTool,
    version: tools_models.DatabaseVersion | None = None,
    nature: tools_models.DatabaseNature | None = None,
    configuration: dict[str, str] | None = None,
) -> models.DatabaseCapellaModel:
    restrictions = restrictions_models.DatabaseToolModelRestrictions()

    model = models.DatabaseCapellaModel(
        name=post_model.name,
        slug=slugify.slugify(post_model.name),
        description=post_model.description if post_model.description else "",
        project=project,
        tool=tool,
        version=version,
        nature=nature,
        restrictions=restrictions,
        configuration=configuration,
    )
    db.add(restrictions)
    db.add(model)
    db.commit()
    return model


def set_tool_for_model(
    db: orm.Session,
    model: models.DatabaseCapellaModel,
    tool: tools_models.DatabaseTool,
) -> models.DatabaseCapellaModel:
    model.tool = tool
    db.commit()
    return model


def set_tool_details_for_model(
    db: orm.Session,
    model: models.DatabaseCapellaModel,
    version: tools_models.DatabaseVersion,
    nature: tools_models.DatabaseNature,
) -> models.DatabaseCapellaModel:
    model.version = version
    model.nature = nature
    db.commit()
    return model


def update_model(
    db: orm.Session,
    model: models.DatabaseCapellaModel,
    description: str | None,
    name: str | None,
    version: tools_models.DatabaseVersion,
    nature: tools_models.DatabaseNature,
    project: projects_model.DatabaseProject,
) -> models.DatabaseCapellaModel:
    model.version = version
    model.nature = nature
    model.project = project
    if description:
        model.description = description
    if name:
        model.name = name
        model.slug = slugify.slugify(name)
    db.commit()
    return model


def delete_model(db: orm.Session, model: models.DatabaseCapellaModel):
    db.delete(model)
    db.commit()
