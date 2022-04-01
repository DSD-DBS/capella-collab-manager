ARG BASE_IMAGE=node:14
FROM $BASE_IMAGE as build

COPY ./ /work/
WORKDIR /work
RUN npm install
RUN npm run build

FROM nginxinc/nginx-unprivileged:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/t4cclient /usr/share/nginx/html