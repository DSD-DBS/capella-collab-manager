# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from . import generate, loader, models

if not loader.does_config_exist():
    generate.write_config()


config = models.AppConfig(**loader.load_yaml())
