# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import capellacollab
from capellacollab.config import config
from capellacollab.settings.configuration import models


def get_metadata(
    global_config: models.GlobalConfiguration,
) -> models.Metadata:
    return models.Metadata.model_validate(
        global_config.metadata.model_dump()
        | {
            "version": capellacollab.__version__,
            "host": config.general.host,
            "port": str(config.general.port),
            "protocol": config.general.scheme,
        }
    )


def get_feedback(
    global_config: models.GlobalConfiguration,
) -> models.FeedbackConfiguration:
    feedback = global_config.feedback
    if not (config.smtp and config.smtp.enabled):
        feedback.enabled = False
        feedback.after_session = False
        feedback.on_footer = False
        feedback.on_session_card = False
        feedback.interval.enabled = False

    return feedback
