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
ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

# Install RDP (XRDP with XORG)
RUN apt-get install -y \ 
    xrdp \ 
    xserver-xorg-core \
    xorgxrdp \
    supervisor \
    openbox \
    obconf \
    nitrogen

COPY rc.xml /etc/xdg/openbox/rc.xml
COPY menu.xml /etc/xdg/openbox/menu.xml

# Setup Nitrogen (Desktop background)
COPY wallpaper.png /tmp/wallpaper.png
COPY bg-saved.cfg /home/techuser/.config/nitrogen/bg-saved.cfg

# Copy Supervisor Configuration
COPY supervisord.conf /etc/supervisord.conf

# Allow any user to start the RDP Server
RUN sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

# Set permissions
RUN chown -R techuser /etc/xrdp/
RUN mkdir -p /run/xrdp/sockdir && chown techuser /run/xrdp/sockdir
RUN chown techuser /var/log/xrdp*

WORKDIR /home/techuser

COPY setup_workspace.py /opt/setup_workspace.py
RUN chown techuser /opt

COPY startup.sh startup.sh
RUN chmod +x startup.sh

USER techuser
ENTRYPOINT [ "/home/techuser/startup.sh" ]