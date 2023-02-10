# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bullseye
FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt upgrade --yes && \
    apt install --yes --no-install-recommends \
    gettext-base \
    locales \
    python3 \
    python3-pip \
    unzip \
    git \
    zip && \
    rm -rf /var/lib/apt/lists/*

ARG UID=1001

COPY docker-entrypoint.sh /

RUN useradd -l -m -u $UID -G users techuser && \
    echo "techuser:tmp_passwd" | chpasswd && \
    chown techuser /home/techuser && \
    mkdir /workspace && \
    chown -R techuser /workspace && \
    chmod +x /docker-entrypoint.sh

RUN python3 -m pip install jupyterlab capellambse

ENV HOME=/home/techuser
ENV JUPYTER_PORT=8888
ENV NOTEBOOKS_DIR=/workspace/notebooks

EXPOSE $JUPYTER_PORT

USER techuser
WORKDIR $HOME

ENTRYPOINT "/docker-entrypoint.sh"
