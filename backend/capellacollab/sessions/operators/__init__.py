# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions.operators.k8s import KubernetesOperator

operator = None


def load_operator():
    global operator
    operator = KubernetesOperator()


def get_operator():
    return operator
