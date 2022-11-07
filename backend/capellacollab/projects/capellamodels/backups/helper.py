# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.sessions.operators import OPERATOR

from .models import Backup, BackupJob, DatabaseBackup


def _inject_last_run(model: DatabaseBackup) -> Backup:
    backup_job = BackupJob(
        id=OPERATOR.get_cronjob_last_run(model.reference),
        date=OPERATOR.get_cronjob_last_starting_date(model.reference),
        state=OPERATOR.get_cronjob_last_state(model.reference),
    )
    return Backup(
        gitmodel=model.gitmodel,
        t4cmodel=model.t4cmodel,
        id=model.id,
        lastrun=backup_job,
    )


def filter_logs(content: str, forbidden_strings: list):
    for forbidden_string in forbidden_strings:
        content = content.replace(forbidden_string, "***********")
