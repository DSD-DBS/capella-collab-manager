# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import capellacollab.sessions.metrics as sessions_metrics
import capellacollab.settings.modelsources.t4c.license_server.metrics as t4c_metrics
from capellacollab.core.database import metrics as database_metrics
from capellacollab.feedback import metrics as feedback_metrics


def register_metrics():
    sessions_metrics.register()
    t4c_metrics.register()
    feedback_metrics.register()
    database_metrics.register()
