# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.sessions.operators.k8s import KubernetesOperator


class OperatorLoader:
    operator = None

    @classmethod
    def load_operator(cls):
        cls.operator = KubernetesOperator()
        cls.operator.load_config()


def get_operator():
    return OperatorLoader.operator
