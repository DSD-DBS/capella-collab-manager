# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

{{- define "capellacollab.pod.spec" }}
{{- if .Values.cluster.podSecurityContext }}
securityContext:
{{ toYaml .Values.cluster.podSecurityContext | indent 2 }}
{{ end }}
{{- end }}
