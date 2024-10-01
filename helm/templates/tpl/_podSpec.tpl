# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

{{- define "capellacollab.pod.spec" }}
{{- if .Values.cluster.podSecurityContext }}
securityContext:
{{ toYaml .Values.cluster.podSecurityContext | indent 2 }}
{{ end }}
{{ if .Values.cluster.nodeSelector }}
nodeSelector:
{{ toYaml .Values.cluster.nodeSelector | indent 2 }}
{{ end }}
{{- end }}
