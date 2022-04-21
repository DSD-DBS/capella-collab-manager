# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from t4cclient.config import OPERATOR_TYPE
from t4cclient.core.operators.abc import Operator

from . import docker, k8s

OPERATORS = {
    "docker": docker.DockerOperator,
    "kubernetes": k8s.KubernetesOperator,
}
try:
    OPERATOR: Operator = OPERATORS[OPERATOR_TYPE]()
except KeyError:
    raise KeyError("Unsupported operator %s", OPERATOR_TYPE) from None
