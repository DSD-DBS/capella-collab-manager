# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=python:3.12-slim-bookworm
FROM $BASE_IMAGE AS build

USER root

RUN pip install -U pip

COPY ./ /opt/docs
WORKDIR /opt/docs

RUN pip install -r requirements.txt && mkdocs build

FROM nginxinc/nginx-unprivileged:latest

USER root
RUN apt-get update \
    && apt-get upgrade --yes \
    && rm -rf /var/lib/apt/lists/*
USER 101

EXPOSE 8080

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /opt/docs/site /usr/share/nginx/html/docs
