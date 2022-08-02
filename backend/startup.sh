#!/bin/bash
set -e

# When running inside the cluster, the k8s service host should not use the proxy
export no_proxy=$no_proxy,$KUBERNETES_SERVICE_HOST
uvicorn t4cclient.__main__:app --host 0.0.0.0