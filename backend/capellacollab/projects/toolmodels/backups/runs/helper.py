# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


def filter_logs(content: str, forbidden_strings: list) -> str:
    for forbidden_string in forbidden_strings:
        content = content.replace(forbidden_string, "***********")
    return content
