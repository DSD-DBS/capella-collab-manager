# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import logging
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import logging as log
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud, models, util

router = fastapi.APIRouter()


@router.post(
    "",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ],
)
def submit_feedback(
    feedback: models.Feedback,
    background_tasks: fastapi.BackgroundTasks,
    user_agent: t.Annotated[str | None, fastapi.Header()] = None,
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    logger: logging.LoggerAdapter = fastapi.Depends(log.get_request_logger),
):
    util.check_if_feedback_is_allowed(db)
    feedback_user = user if feedback.share_contact else None

    crud.save_feedback(
        db,
        feedback.rating,
        feedback_user,
        feedback.feedback_text,
        datetime.datetime.now(),
        feedback.trigger,
    )

    background_tasks.add_task(
        util.send_feedback_email,
        db,
        feedback,
        (
            users_models.User.model_validate(feedback_user)
            if feedback_user
            else None
        ),
        user_agent,
        logger,
    )
