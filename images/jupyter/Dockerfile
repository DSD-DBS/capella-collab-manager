# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bullseye
FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    gettext-base \
    locales \
    python3 \
    python3-pip \
    unzip \
    git \
    zip && \
    rm -rf /var/lib/apt/lists/*

ARG UID=1001

RUN useradd -l -m -u $UID -G users techuser && \
    echo "techuser:tmp_passwd" | chpasswd && \
    chown techuser /home/techuser && \
    mkdir /workspace && \
    chown -R techuser /workspace

RUN python3 -m pip install jupyterlab capellambse

ENV HOME=/home/techuser
ENV JUPYTER_PORT=8888

EXPOSE $JUPYTER_PORT

USER techuser
WORKDIR $HOME

CMD jupyter-lab --ip=0.0.0.0 \
    --port=$JUPYTER_PORT \
    --no-browser \
    --ServerApp.base_url=$JUPYTER_BASE_URL \
    --ServerApp.root_dir=/workspace/
