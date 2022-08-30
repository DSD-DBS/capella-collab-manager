ARG BASE_IMAGE=node:17
FROM $BASE_IMAGE as build

ARG CONFIGURATION=development

COPY ./ /work/
WORKDIR /work
RUN npm install
RUN npm run build -- --configuration=${CONFIGURATION}

FROM nginxinc/nginx-unprivileged:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/t4cclient /usr/share/nginx/html
