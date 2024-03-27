# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG ALPINE_BASE_IMAGE=alpine:latest
FROM ${ALPINE_BASE_IMAGE}

COPY clone_repositories.py /opt/clone_repositories.py
RUN apk add --no-cache git git-lfs python3 py3-pip

ENTRYPOINT [ "python3", "/opt/clone_repositories.py" ]
