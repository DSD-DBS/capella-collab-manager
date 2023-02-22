# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import functools

from capellacollab.sessions.operators.k8s import KubernetesOperator


@functools.lru_cache
def get_operator():
    return KubernetesOperator()
