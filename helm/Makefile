# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

template:
	helm template . \
		--set mocks.oauth=True \
		--set mocks.smtp=True \
		--set backend.authentication.claimMapping.username=sub \
		--set backend.authentication.endpoints.authorization=https://localhost/default/authorize \
		--set cluster.ingressClassName=traefik \
		--set cluster.ingressNamespace=kube-system \
		--set loki.gateway.basicAuth.password="localLokiPassword" \
		--set grafana.adminPassword="admin" \
		--set database.backend.internal.password="secret" \
		--set database.guacamole.internal.password="secret" \
		--set valkey.password="secret"
