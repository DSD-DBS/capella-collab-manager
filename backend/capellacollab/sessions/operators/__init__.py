# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from importlib import metadata

from capellacollab.config import config
from capellacollab.sessions.operators.k8s import KubernetesOperator

OPERATOR = KubernetesOperator()


def get_operator():
    return OPERATOR
