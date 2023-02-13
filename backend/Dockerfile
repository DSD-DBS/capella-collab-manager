# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=python:3.11-bullseye
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    unzip \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl if not available in base image
# kubectl is needed for the list files endpoint
RUN kubectl_installed="yes"; dpkg -s kubectl || kubectl_installed="no"; \
    if [[ "$kubectl_installed" == "no" ]]; \
    then \
    curl -fsSLo /usr/share/keyrings/kubectl.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg; \
    echo "deb [signed-by=/usr/share/keyrings/kubectl.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list; \
    apt-get update && apt-get install -y kubectl && rm -rf /var/lib/apt/lists/*; \
    fi

EXPOSE 8000
COPY . /tmp/backend
COPY .git_archival.txt /tmp/.git_archival.txt
COPY startup.sh /opt/.startup.sh

WORKDIR /tmp/backend
RUN pip install ".[psycopg2]"

RUN mkdir -p /var/log/backend && \
    chmod -R 777 /var/log/backend

# Mount a config.yaml into this directory
VOLUME [ "/etc/capellacollab" ]

RUN chmod 777 /opt/.startup.sh
CMD ["/opt/.startup.sh"]
