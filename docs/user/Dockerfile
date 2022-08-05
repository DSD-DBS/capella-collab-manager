ARG BASE_IMAGE=python:3.10
FROM $BASE_IMAGE as build

RUN pip install -U pip && \
    pip install mkdocs-material

COPY ./ /opt/docs
WORKDIR /opt/docs
RUN mkdocs build

FROM nginxinc/nginx-unprivileged:latest

EXPOSE 80

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /opt/docs/site /usr/share/nginx/html
