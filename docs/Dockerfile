# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=python:3.11-bookworm
FROM $BASE_IMAGE as build

USER root

RUN pip install -U pip && \
    pip install mkdocs-material

COPY ./ /opt/docs
WORKDIR /opt/docs
RUN mkdocs build

FROM nginxinc/nginx-unprivileged:latest

EXPOSE 8080

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /opt/docs/site /usr/share/nginx/html/docs
