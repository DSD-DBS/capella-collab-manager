# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "").lower() in (
    "1",
    "true",
    "t",
)
