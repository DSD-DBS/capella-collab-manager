#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -e

# When running inside the cluster, the k8s service host should not use the proxy
export no_proxy=$no_proxy,$KUBERNETES_SERVICE_HOST,$no_proxy_additional
uvicorn t4cclient.__main__:app --host 0.0.0.0
