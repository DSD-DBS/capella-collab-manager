#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -e

# When running inside the cluster, the k8s service host should not use the proxy
export no_proxy=$no_proxy,$KUBERNETES_SERVICE_HOST,$no_proxy_additional,svc.cluster.local
export NO_PROXY=$NO_PROXY,$KUBERNETES_SERVICE_HOST,$no_proxy_additional,svc.cluster.local

if [ "$1" = "scheduler" ]; then
    /opt/backend/.venv/bin/python -m capellacollab.cli scheduler run
else
    /opt/backend/.venv/bin/python -m capellacollab.__main__
fi
