# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions.operators.k8s import KubernetesOperator

operator = None


def get_operator():
    global operator

    if not operator:
        operator = KubernetesOperator()
        operator.load_config()

    return operator
