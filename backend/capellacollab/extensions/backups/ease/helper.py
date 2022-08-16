# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# local:
from . import models

# 1st party:
from capellacollab.core.operators import OPERATOR
from capellacollab.sessions.operators import OPERATOR


def _inject_last_run(model: models.DB_EASEBackup) -> models.EASEBackupResponse:
    backup_job = models.EASEBackupJob(
        id=OPERATOR.get_cronjob_last_run(model.reference),
        date=OPERATOR.get_cronjob_last_starting_date(model.reference),
        state=OPERATOR.get_cronjob_last_state(model.reference),
    )
    return models.EASEBackupResponse(
        gitmodel=model.gitmodel,
        t4cmodel=model.t4cmodel,
        id=model.id,
        lastrun=backup_job,
    )
