# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=node:17
FROM $BASE_IMAGE as build

ARG CONFIGURATION=production

COPY ./ /work/
WORKDIR /work
RUN npm install
RUN npm run build -- --configuration=${CONFIGURATION}

FROM nginxinc/nginx-unprivileged:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/t4cclient /usr/share/nginx/html
