# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=node:22
FROM $BASE_IMAGE as build

USER root

ARG CONFIGURATION=production
RUN npm install -g corepack@latest && corepack enable

WORKDIR /work

COPY ./package.json /work/
COPY ./pnpm-lock.yaml /work/
RUN pnpm install --ignore-scripts

COPY . /work
RUN pnpm run build -- --configuration=${CONFIGURATION}

FROM nginxinc/nginx-unprivileged:latest

EXPOSE 8080

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/capellacollab /usr/share/nginx/html
USER root
RUN chmod -R 777 /var/log/nginx
USER nginx
