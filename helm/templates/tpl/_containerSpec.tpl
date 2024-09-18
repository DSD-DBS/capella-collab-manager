# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

{{- define "capellacollab.container.spec" }}
imagePullPolicy: {{ .Values.cluster.imagePullPolicy }}
{{- end }}
