# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG DEBIAN_SLIM_BASE_IMAGE=debian:bookworm-slim
FROM ${DEBIAN_SLIM_BASE_IMAGE} as build-extension
USER root

RUN apt-get update && apt-get install -y zip
COPY ext /tmp/ext

WORKDIR /tmp/ext
RUN zip -r /tmp/guacamole-capellacollab.jar .

FROM guacamole/guacamole:1.6.0

USER root

COPY guacamole.properties /etc/guacamole/guacamole.properties
COPY --from=build-extension /tmp/guacamole-capellacollab.jar /etc/guacamole/extensions/

RUN mkdir -p /etc/guacamole && \
    chmod -R 777 \
    /opt/guacamole \
    /usr/local/tomcat/webapps \
    /home/guacamole \
    /etc/guacamole

ENV HOME=/home/guacamole
ENV JAVA_OPTS="-Duser.home=/home/guacamole"
ENV GUACAMOLE_HOME=/etc/guacamole
