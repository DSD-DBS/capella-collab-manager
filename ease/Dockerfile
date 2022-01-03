# Copyright 2021 DB Netz AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
ARG BUILD_TYPE=offline
ARG BASE_IMAGE=capella/base

FROM $BASE_IMAGE as prebuild

RUN apt install -y openjdk-17-jre xdg-utils xvfb dbus-x11

# Use Virtual Display
ENV DISPLAY :99

RUN pip install py4j

# Offline build (fixed version)
FROM prebuild as build_offline
ONBUILD COPY ease/extensions /tmp/extensions 
ONBUILD ENV PY4J_REPOSITORY=file:/tmp/extensions/py4j
ONBUILD ENV EASE_REPOSITORY=file:/tmp/extensions/ease
ONBUILD ENV SWTBOT_REPOSITORY=file:/tmp/extensions/swtbot

# Online build (latest version)
FROM prebuild as build_online
ONBUILD ENV PY4J_REPOSITORY=https://eclipse.py4j.org/
ONBUILD ENV EASE_REPOSITORY=https://download.eclipse.org/ease/integration/nightly
ONBUILD ENV SWTBOT_REPOSITORY=https://download.eclipse.org/technology/swtbot/releases/latest/

FROM build_${BUILD_TYPE}

# Install EASE Dependencies
# - org.py4j.feature.feature.group
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${PY4J_REPOSITORY} \
    -installIU org.py4j.feature.feature.group

# Install EASE
# Following Plugins will be installed: 
# - EASE Core Framework (Incubation)	        org.eclipse.ease.feature.feature.group	                    Eclipse.org
# - EASE UI Components (Incubation)	            org.eclipse.ease.ui.feature.feature.group	                Eclipse.org
# - EASE Py4J Support (Incubation)	            org.eclipse.ease.lang.python.py4j.feature.feature.group	    Eclipse.org
# - EASE Python Support (Incubation)	        org.eclipse.ease.lang.python.feature.feature.group	        Eclipse.org
# - EASE Git Feature (Incubation)	            org.eclipse.ease.modules.team.git.feature.feature.group	    Eclipse.org
# - EASE Modules (Incubation)	                org.eclipse.ease.modules.feature.feature.group	            Eclipse.org
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${EASE_REPOSITORY} \
    -installIU org.eclipse.ease.feature.feature.group,org.eclipse.ease.ui.feature.feature.group,org.eclipse.ease.lang.python.py4j.feature.feature.group,org.eclipse.ease.lang.python.feature.feature.group,org.eclipse.ease.modules.team.git.feature.feature.group,org.eclipse.ease.modules.feature.feature.group

# Install SWTBot
# Following Plugins will be installed: 
# - SWTBot for Eclipse Forms Testing	    org.eclipse.swtbot.forms.feature.group	            Eclipse.org - SWTBot
# - SWTBot for Eclipse Testing	            org.eclipse.swtbot.eclipse.feature.group	        Eclipse.org - SWTBot
# - SWTBot for GEF Testing	                org.eclipse.swtbot.eclipse.gef.feature.group	    Eclipse.org - SWTBot
# - SWTBot for SWT Testing	                org.eclipse.swtbot.feature.group	                Eclipse.org - SWTBot
# - SWTBot IDE Features	                    org.eclipse.swtbot.ide.feature.group	            Eclipse.org - SWTBot
# - SWTBot Test Recorder and Code Generator	org.eclipse.swtbot.generator.feature.feature.group	Eclipse.org - SWTBot
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${SWTBOT_REPOSITORY} \
    -installIU org.eclipse.swtbot.forms.feature.group,org.eclipse.swtbot.eclipse.feature.group,org.eclipse.swtbot.eclipse.gef.feature.group,org.eclipse.swtbot.feature.group,org.eclipse.swtbot.ide.feature.group,org.eclipse.swtbot.generator.feature.feature.group

RUN rm -rf /tmp/extensions
RUN echo "-Dorg.eclipse.swtbot.search.timeout=1000" >> /opt/capella/capella.ini

COPY ease/pyease /tmp/pyease
RUN pip install /tmp/pyease

ENV EASE_WORKSPACE /workspace
ENV EASE_SCRIPTS_LOCATION /opt/scripts
ENV EASE_LOG_LOCATION=/proc/1/fd/1

RUN mkdir /opt/scripts && \ 
    chown techuser /opt/scripts

# Clean Workspace and set it up for EASE
RUN python -m pyease.ease
RUN chown -R techuser /workspace

WORKDIR /home/techuser

COPY ease/startup.sh /opt/startup.sh
RUN chmod +x /opt/startup.sh
ENTRYPOINT [ "/opt/startup.sh" ]
