# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import capellacollab
from capellacollab import core
from capellacollab.configuration.app import config

from . import models


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


def get_navbar(
    global_config: models.GlobalConfiguration,
) -> models.NavbarConfiguration:
    navbar_config = global_config.navbar

    if navbar_config.badge.show:
        if navbar_config.badge.text == "auto":
            if core.CLUSTER_DEVELOPMENT_MODE:
                navbar_config.badge.text = "Cluster Development"
            elif core.LOCAL_DEVELOPMENT_MODE:
                navbar_config.badge.text = "Local Development"
            else:
                navbar_config.badge.text = (
                    global_config.metadata.environment or "Unknown Environment"
                )

        if navbar_config.badge.variant == models.BadgeVariant.AUTO:
            words = ["dev", "development", "unknown", "staging"]
            if any(word in navbar_config.badge.text.lower() for word in words):
                navbar_config.badge.variant = models.BadgeVariant.WARNING
            else:
                navbar_config.badge.variant = models.BadgeVariant.SUCCESS

    return navbar_config
