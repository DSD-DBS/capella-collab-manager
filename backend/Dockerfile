# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=python:3.12-slim-bookworm
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    git-lfs \
    libpq-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
COPY . /tmp/backend
COPY .git_archival.txt /tmp/.git_archival.txt
COPY startup.sh /opt/.startup.sh

# Activate venv
RUN ln -s "$(which python3.12)" /usr/bin/python && \
    ln -sf "$(which python3.12)" /usr/bin/python3 && \
    python -m venv /opt/.venv
ENV _OLD_VIRTUAL_PATH="$PATH"
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /tmp/backend
RUN pip install . && chmod +x "$VIRTUAL_ENV/lib/python3.12/site-packages/capellacollab/settings/modelsources/git/askpass.py"

RUN mkdir -p /var/log/backend && \
    chmod -R 777 /var/log/backend

# Mount a config.yaml into this directory
VOLUME [ "/etc/capellacollab" ]

RUN chmod 777 /opt/.startup.sh
CMD ["/opt/.startup.sh"]
