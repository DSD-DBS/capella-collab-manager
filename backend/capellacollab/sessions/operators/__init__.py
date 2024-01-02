# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import functools

from capellacollab.sessions.operators.k8s import KubernetesOperator


@functools.lru_cache
def get_operator():
    return KubernetesOperator()
