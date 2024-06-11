# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    unzip \
    libpq-dev \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    gnupg \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

ARG KUBECTL_APT_REMOTE=https://pkgs.k8s.io/core:/stable:/v1.29/deb/

# Install kubectl if not available in base image
# kubectl is needed for the list files endpoint
RUN mkdir -p /etc/apt/keyrings && \
    curl --proto "=https" -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] $KUBECTL_APT_REMOTE /" | tee /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && apt-get install -y kubectl && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
COPY . /tmp/backend
COPY .git_archival.txt /tmp/.git_archival.txt
COPY startup.sh /opt/.startup.sh

# Activate venv
RUN ln -s $(which python3.11) /usr/bin/python && \
    ln -sf $(which python3.11) /usr/bin/python3 && \
    python -m venv /opt/.venv
ENV _OLD_VIRTUAL_PATH="$PATH"
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /tmp/backend
RUN pip install . && chmod +x $VIRTUAL_ENV/lib/python3.11/site-packages/capellacollab/settings/modelsources/git/askpass.py

RUN mkdir -p /var/log/backend && \
    chmod -R 777 /var/log/backend

# Mount a config.yaml into this directory
VOLUME [ "/etc/capellacollab" ]

RUN chmod 777 /opt/.startup.sh
CMD ["/opt/.startup.sh"]
