# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.sessions.operators import OPERATOR

from .models import DB_EASEBackup, EASEBackupJob, EASEBackupResponse


def _inject_last_run(model: DB_EASEBackup) -> EASEBackupResponse:
    backup_job = EASEBackupJob(
        id=OPERATOR.get_cronjob_last_run(model.reference),
        date=OPERATOR.get_cronjob_last_starting_date(model.reference),
        state=OPERATOR.get_cronjob_last_state(model.reference),
    )
    return EASEBackupResponse(
        gitmodel=model.gitmodel,
        t4cmodel=model.t4cmodel,
        id=model.id,
        lastrun=backup_job,
    )


def filter_logs(content: str, forbidden_strings: list):
    for forbidden_string in forbidden_strings:
        content = content.replace(forbidden_string, "***********")
