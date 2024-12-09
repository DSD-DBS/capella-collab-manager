# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=node:22
FROM $BASE_IMAGE as build

USER root

ARG CONFIGURATION=production
RUN npm install -g npm@latest

WORKDIR /work

COPY ./package*.json /work/
RUN npm i

COPY . /work
RUN npm run build -- --configuration=${CONFIGURATION}

FROM nginxinc/nginx-unprivileged:latest

EXPOSE 8080

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/capellacollab /usr/share/nginx/html
USER root
RUN chmod -R 777 /var/log/nginx
USER nginx
