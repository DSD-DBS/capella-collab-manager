# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

{{- define "capellacollab.promtail.default.config" }}
clients:
  - url: http://loki-gateway.{{- .Release.Namespace -}}.svc.cluster.local/loki/api/v1/push
    basic_auth:
      username: {{ .Values.definitions.loki.username }}
      password: {{ .Values.definitions.loki.password }}
server:
  http_listen_port: 3101
{{- end }}
