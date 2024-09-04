# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.feedback.models import Feedback
from capellacollab.feedback.util import is_feedback_allowed, send_email
from capellacollab.settings.configuration import core as config_core
from capellacollab.settings.configuration import (
    models as settings_config_models,
)
from capellacollab.settings.configuration.models import FeedbackConfiguration
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

router = fastapi.APIRouter()


@router.get(
    "/feedback",
    response_model=FeedbackConfiguration,
)
def get_feedback(db: orm.Session = fastapi.Depends(database.get_db)):
    cfg = config_core.get_config(db, "global")
    assert isinstance(cfg, settings_config_models.GlobalConfiguration)

    return FeedbackConfiguration.model_validate(cfg.feedback.model_dump())


@router.post("/feedback")
def submit_feedback(
    feedback: Feedback,
    background_tasks: fastapi.BackgroundTasks,
    user_agent: t.Annotated[str | None, fastapi.Header()] = None,
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    is_feedback_allowed(db)
    background_tasks.add_task(send_email, feedback, user, user_agent, db)
    return {"status": "sending"}
