# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.tools import models as tools_models

from . import exceptions, models


def get_tools(db: orm.Session) -> abc.Sequence[models.DatabaseTool]:
    return db.execute(sa.select(models.DatabaseTool)).scalars().all()


def get_tool_by_id(
    db: orm.Session, tool_id: int
) -> models.DatabaseTool | None:
    return db.execute(
        sa.select(models.DatabaseTool).where(models.DatabaseTool.id == tool_id)
    ).scalar_one_or_none()


def get_tool_by_name(
    db: orm.Session, tool_name: str
) -> models.DatabaseTool | None:
    return db.execute(
        sa.select(models.DatabaseTool).where(
            models.DatabaseTool.name == tool_name
        )
    ).scalar_one_or_none()


def get_compatible_versions_for_tool_versions(
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
) -> list[tools_models.DatabaseVersion]:
    return [
        res_tool_version
        for res_tool_version in get_versions(db)
        if res_tool_version.id in tool_version.config.compatible_versions
    ]


def create_tool(
    db: orm.Session, tool: models.CreateTool
) -> models.DatabaseTool:
    database_tool = tools_models.DatabaseTool(
        name=tool.name,
        integrations=tool.integrations,
        config=tool.config,
    )
    db.add(database_tool)
    db.commit()
    return database_tool


def update_tool(
    db: orm.Session, tool: models.DatabaseTool, updated_tool: models.CreateTool
) -> models.DatabaseTool:
    tool.name = updated_tool.name
    tool.integrations = updated_tool.integrations
    tool.config = updated_tool.config
    db.commit()
    return tool


def delete_tool(db: orm.Session, tool: models.DatabaseTool) -> None:
    db.delete(tool)
    db.commit()


def get_versions(db: orm.Session) -> abc.Sequence[models.DatabaseVersion]:
    return db.execute(sa.select(models.DatabaseVersion)).scalars().all()


def get_versions_for_tool_id(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.DatabaseVersion]:
    return (
        db.execute(
            sa.select(models.DatabaseVersion).where(
                models.DatabaseVersion.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def get_version_by_id(
    db: orm.Session, version_id: int
) -> models.DatabaseVersion | None:
    return db.execute(
        sa.select(models.DatabaseVersion).where(
            models.DatabaseVersion.id == version_id
        )
    ).scalar_one_or_none()


def get_version_by_version_and_tool_id(
    db: orm.Session, tool_id: int, version_id: int
) -> models.DatabaseVersion | None:
    return db.execute(
        sa.select(models.DatabaseVersion)
        .where(models.DatabaseVersion.id == version_id)
        .where(models.DatabaseVersion.tool_id == tool_id)
    ).scalar_one_or_none()


def get_version_by_tool_id_version_name(
    db: orm.Session, tool_id: int, version_name: str
) -> models.DatabaseVersion | None:
    return db.execute(
        sa.select(models.DatabaseVersion)
        .where(models.DatabaseVersion.tool_id == tool_id)
        .where(models.DatabaseVersion.name == version_name)
    ).scalar_one_or_none()


def update_version(
    db: orm.Session,
    version: models.DatabaseVersion,
    updated_version: models.CreateToolVersion,
) -> models.DatabaseVersion:
    version.name = updated_version.name
    version.config = updated_version.config

    db.commit()
    return version


def create_version(
    db: orm.Session,
    tool: models.DatabaseTool,
    tool_version: models.CreateToolVersion,
) -> models.DatabaseVersion:
    version = models.DatabaseVersion(
        name=tool_version.name,
        config=tool_version.config,
        tool=tool,
    )
    db.add(version)
    db.commit()
    return version


def delete_tool_version(
    db: orm.Session, version: models.DatabaseVersion
) -> None:
    db.delete(version)
    db.commit()


def get_nature_for_tool(
    db: orm.Session, tool_id: int, nature_id: int
) -> models.DatabaseNature | None:
    return db.execute(
        sa.select(models.DatabaseNature)
        .where(models.DatabaseNature.id == nature_id)
        .where(models.DatabaseNature.tool_id == tool_id)
    ).scalar_one_or_none()


def get_nature_by_name(
    db: orm.Session, tool: models.DatabaseTool, name: str
) -> models.DatabaseNature | None:
    return db.execute(
        sa.select(models.DatabaseNature)
        .where(models.DatabaseNature.tool == tool)
        .where(models.DatabaseNature.name == name)
    ).scalar_one_or_none()


def get_natures(db: orm.Session) -> abc.Sequence[models.DatabaseNature]:
    return db.execute(sa.select(models.DatabaseNature)).scalars().all()


def get_nature_by_id(
    db: orm.Session, nature_id: int
) -> models.DatabaseNature | None:
    return db.execute(
        sa.select(models.DatabaseNature).where(
            models.DatabaseNature.id == nature_id
        )
    ).scalar_one_or_none()


def get_natures_by_tool_id(
    db: orm.Session, tool_id: int
) -> abc.Sequence[models.DatabaseNature]:
    return (
        db.execute(
            sa.select(models.DatabaseNature).where(
                models.DatabaseNature.tool_id == tool_id
            )
        )
        .scalars()
        .all()
    )


def update_nature(
    db: orm.Session,
    nature: models.DatabaseNature,
    updated_version: models.CreateToolNature,
) -> models.DatabaseNature:
    nature.name = updated_version.name

    db.commit()
    return nature


def create_nature(
    db: orm.Session, tool: models.DatabaseTool, name: str
) -> models.DatabaseNature:
    nature = models.DatabaseNature(name=name, tool=tool)
    db.add(nature)
    db.commit()
    return nature


def delete_nature(db: orm.Session, nature: models.DatabaseNature) -> None:
    db.delete(nature)
    db.commit()


def get_backup_image_for_tool_version(db: orm.Session, version_id: int) -> str:
    """
    Retrieve the backup image template for a specific tool version and replace the placeholder with the tool's version name.

    The function first checks if the provided version_id corresponds to an existing tool version in the database.
    If not, it raises a ToolVersionNotFoundError. Then, it retrieves the tool's backup image template.
    If the backup image template does not exist, it raises a ToolImageNotFoundError.

    Finally, it replaces the placeholder "$version" in the backup image template with the actual version name and returns it.

    Args
    ----
    db : orm.Session
        The database session to use for database operations.
    version_id : int
        The ID of the tool version for which to get the backup image.

    Returns
    -------
    str:
        The backup image name for the specified tool version. The "$version" placeholder in the template
        is replaced with the actual version name.

    Raises
    ------
    ToolVersionNotFoundError
        If a tool version with the specified version_id does not exist.
    ToolImageNotFoundError
        If the tool corresponding to the version does not have an associated backup image template.
    """
    if not (version := get_version_by_id(db, version_id)):
        raise exceptions.ToolVersionNotFoundError(version_id)

    backup_image_template = version.config.backups.image

    if not backup_image_template:
        raise exceptions.ToolImageNotFoundError(
            tool_id=version.tool.id, image_name="backup"
        )

    return backup_image_template.format(version=version.name)


def remove_tool_version_from_compatible_versions_config(
    db: orm.Session,
    tool_version_to_update: models.DatabaseVersion,
    tool_version_to_remove: models.DatabaseVersion,
):
    tool_version_to_update.config.compatible_versions.remove(
        tool_version_to_remove.id
    )
    orm.attributes.flag_modified(tool_version_to_update, "config")
    db.commit()
