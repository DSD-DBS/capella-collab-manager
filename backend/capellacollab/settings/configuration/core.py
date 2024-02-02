# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import orm

from . import crud, models


def get_config(db: orm.Session, name: str) -> models.ConfigurationBase:
    """Get a configuration by name."""
    configuration = crud.get_configuration_by_name(db, name)
    model_type = models.NAME_TO_MODEL_TYPE_MAPPING[name]
    if configuration:
        return model_type().model_validate(configuration.configuration)
    return model_type().model_validate({})
