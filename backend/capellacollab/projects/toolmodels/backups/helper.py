# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from .models import Backup, DatabaseBackup


def _inject_last_run(model: DatabaseBackup) -> Backup:
    return model


def filter_logs(content: str, forbidden_strings: list) -> str:
    for forbidden_string in forbidden_strings:
        content = content.replace(forbidden_string, "***********")
    return content
