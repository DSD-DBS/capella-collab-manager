#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -e

# When running inside the cluster, the k8s service host should not use the proxy
export no_proxy=$no_proxy,$KUBERNETES_SERVICE_HOST,$no_proxy_additional,svc.cluster.local
export NO_PROXY=$NO_PROXY,$KUBERNETES_SERVICE_HOST,$no_proxy_additional,svc.cluster.local
/opt/backend/.venv/bin/uvicorn capellacollab.__main__:app --host 0.0.0.0 --forwarded-allow-ips '*'
