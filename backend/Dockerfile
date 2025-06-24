# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

EXPOSE 8000

USER root

ADD https://astral.sh/uv/install.sh /uv-installer.sh
ENV UV_UNMANAGED_INSTALL=/usr/bin/
ENV UV_PYTHON_INSTALL_DIR=/etc/python

RUN apt-get update \
    && apt-get upgrade --yes \
    && apt-get install --yes \
    ca-certificates \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/usr/bin/:$PATH"
WORKDIR /opt/backend

RUN uv python install 3.12 --preview \
    && ln -s /etc/python/cpython-3.12-*/bin/python /usr/bin/python \
    && ln -s /etc/python/cpython-3.12-*/bin/python /usr/bin/python3 \
    && uv venv

COPY . /opt/backend
COPY .git_archival.txt /opt/.git_archival.txt
COPY startup.sh /opt/.startup.sh

RUN uv pip install . && chmod +x ".venv/lib/python3.12/site-packages/capellacollab/settings/modelsources/git/askpass.py" \
    && mkdir -p /var/log/backend \
    && chmod -R 777 /var/log/backend \
    && chmod 777 /opt/.startup.sh \
    && chmod -R 777 /opt/backend

# Mount a config.yaml into this directory
VOLUME [ "/etc/capellacollab" ]

USER 1001

ENTRYPOINT ["/opt/.startup.sh"]
