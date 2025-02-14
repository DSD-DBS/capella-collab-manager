# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime


def on_config(config, **kwargs):
    config.copyright = (
        f"Copyright &copy; 2022-{datetime.datetime.now(tz=datetime.UTC).year} DB InfraGO AG"
    )
