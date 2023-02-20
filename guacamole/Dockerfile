# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

FROM guacamole/guacamole:1.5.0

USER root
RUN chmod -R 777 \
    /opt/guacamole \
    /usr/local/tomcat/webapps \
    /home/guacamole

ENV HOME=/home/guacamole
ENV JAVA_OPTS="-Duser.home=/home/guacamole"
