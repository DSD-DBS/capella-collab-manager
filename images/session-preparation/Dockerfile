# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG ALPINE_BASE_IMAGE=alpine:latest
FROM ${ALPINE_BASE_IMAGE}

USER root

COPY clone_repositories.py /opt/clone_repositories.py
RUN apk add --no-cache \
    git \
    git-lfs \
    py3-pip \
    python3

COPY git_askpass.py /etc/git_askpass.py
RUN chmod 555 /etc/git_askpass.py

USER 1001

ENTRYPOINT [ "python3", "/opt/clone_repositories.py" ]
