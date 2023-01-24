# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=python:3.11-bullseye
FROM $BASE_IMAGE

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    ca-certificates \
    unzip \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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
