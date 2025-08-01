# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.logging import injectables as logging_injectables
from capellacollab.feedback import util as feedback_util
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.toolmodels.backups import (
    interface as pipelines_interface,
)
from capellacollab.users import crud as users_crud

from . import core, crud, models, util

router = fastapi.APIRouter(
    tags=["Configuration"],
)


@router.get(
    "/unified",
)
def get_unified_config(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.UnifiedConfig:
    cfg = core.get_global_configuration(db)

    return models.UnifiedConfig(
        metadata=util.get_metadata(cfg),
        feedback=util.get_feedback(cfg),
        beta=cfg.beta,
        navbar=util.get_navbar(cfg),
    )


@router.get(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        configuration={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_configuration(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    return core.get_global_configuration(db)


@router.put(
    f"/{models.GlobalConfiguration._name}",
    response_model=models.GlobalConfiguration,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        configuration={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def update_configuration(
    body: models.GlobalConfiguration,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    logger: t.Annotated[
        logging.LoggerAdapter,
        fastapi.Depends(logging_injectables.get_request_logger),
    ],
):
    configuration = crud.get_configuration_by_name(
        db, models.GlobalConfiguration._name
    )

    feedback_util.validate_global_configuration(body.feedback)

    if body.beta.enabled is False:
        users_crud.unenroll_all_beta_testers(db)

    if body.feedback.enabled is False:
        feedback_util.disable_feedback(body.feedback)

    if configuration:
        try:
            validated_config = models.GlobalConfiguration.model_validate(
                configuration
            )
        except pydantic.ValidationError:
            logger.exception(
                "Failed to validate existing configuration. Assuming default values."
            )
            validated_config = models.GlobalConfiguration()

        if body.pipelines != validated_config.pipelines:
            pipelines_interface.update_trigger_configuration(body.pipelines)

        return crud.update_configuration(
            db, configuration, body.model_dump()
        ).configuration
    if body.pipelines != models.GlobalConfiguration().pipelines:
        pipelines_interface.update_trigger_configuration(body.pipelines)

    return crud.create_configuration(
        db,
        name=models.GlobalConfiguration._name,
        configuration=body.model_dump(),
    ).configuration


@router.get(
    f"/{models.GlobalConfiguration._name}/schema", response_model=t.Any
)
def get_json_schema():
    return models.GlobalConfiguration.model_json_schema()
