# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from . import models


def get_configuration_by_name(
    db: orm.Session, name: str
) -> None | models.DatabaseConfiguration:
    return db.execute(
        sa.select(models.DatabaseConfiguration).where(
            models.DatabaseConfiguration.name == name
        )
    ).scalar_one_or_none()


def get_pydantic_configuration_by_name(
    db: orm.Session, pydantic_model: models.ConfigurationBase
):
    return pydantic_model.model_validate(
        get_configuration_by_name(db, pydantic_model._name)
    )


def create_configuration(
    db: orm.Session,
    name: str,
    configuration: dict[str, str],
) -> models.DatabaseConfiguration:
    db_configuration = models.DatabaseConfiguration(
        name=name, configuration=configuration
    )
    db.add(db_configuration)
    db.commit()
    return db_configuration


def update_configuration(
    db: orm.Session,
    db_configuration: models.DatabaseConfiguration,
    configuration: dict[str, str],
) -> models.DatabaseConfiguration:
    db_configuration.configuration = configuration
    db.commit()
    return db_configuration


def delete_configuration(
    db: orm.Session, db_configuration: models.DatabaseConfiguration
):
    db.delete(db_configuration)
    db.commit()
