# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from . import models


def filter_logs(
    logs: list[models.PipelineLogLine], forbidden_strings: list[str]
):
    for line in logs:
        for forbidden_string in forbidden_strings:
            line.text = line.text.replace(forbidden_string, "***********")
