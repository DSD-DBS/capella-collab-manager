# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=node:22
FROM $BASE_IMAGE AS build

USER root

ARG CONFIGURATION=production
RUN npm install -g corepack@latest && corepack enable

WORKDIR /work

COPY ./package.json /work/
COPY ./pnpm-lock.yaml /work/
RUN pnpm install --ignore-scripts

COPY . /work
RUN pnpm run build -- --configuration=${CONFIGURATION}

FROM caddy:2.9-alpine

EXPOSE 8080

RUN apk --no-cache upgrade \
    && adduser -S appuser \
    && mkdir -p /var/log \
                /data/caddy/locks \
                /config/caddy \
    && touch /var/log/access.log \
    && chown -R appuser /var/log /data /config /srv /etc/caddy /usr/bin/caddy \
    && chmod 666 /var/log/access.log \
    && chmod -R 770 /data/caddy /config/caddy \
    && chmod 755 /usr/bin/caddy

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /work/dist/capellacollab /srv

USER appuser
