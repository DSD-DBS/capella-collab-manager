# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

{{- define "capellacollab.promtail.default.config" }}
clients:
  - url: http://{{.Release.Name}}-loki-gateway.{{- .Release.Namespace -}}.svc.cluster.local/loki/api/v1/push
    basic_auth:
      username: {{ .Values.loki.gateway.basicAuth.username }}
      password: {{ .Values.loki.gateway.basicAuth.password }}
server:
  http_listen_port: 3101
{{- end }}
