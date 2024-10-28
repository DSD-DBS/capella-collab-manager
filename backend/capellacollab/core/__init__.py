# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os

CLUSTER_DEVELOPMENT_MODE: bool = os.getenv(
    "CLUSTER_DEVELOPMENT_MODE", ""
).lower() in (
    "1",
    "true",
    "t",
)

LOCAL_DEVELOPMENT_MODE: bool = os.getenv(
    "LOCAL_DEVELOPMENT_MODE", ""
).lower() in (
    "1",
    "true",
    "t",
)

DEVELOPMENT_MODE = LOCAL_DEVELOPMENT_MODE or CLUSTER_DEVELOPMENT_MODE
