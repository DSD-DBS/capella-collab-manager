ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

# Install RDP (XRDP with XORG)
RUN apt-get -y install xrdp
RUN apt-get -y install xserver-xorg-core xorgxrdp

# Supervisor Installation
RUN apt-get -y install supervisor

# Install Window Manager
RUN apt-get -y install openbox obconf
COPY remote/rc.xml /etc/xdg/openbox/rc.xml
COPY remote/menu.xml /etc/xdg/openbox/menu.xml

# Install Nitrogen (Desktop background)
RUN apt-get -y install nitrogen
COPY remote/wallpaper.png /tmp/wallpaper.png
COPY remote/bg-saved.cfg /home/techuser/.config/nitrogen/bg-saved.cfg

# Copy Supervisor Configuration
COPY remote/supervisord.conf /etc/supervisord.conf

# Allow any user to start the RDP Server
RUN sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

# Set permissions
RUN chown -R techuser /etc/xrdp/
RUN mkdir -p /run/xrdp/sockdir && chown techuser /run/xrdp/sockdir
RUN chown techuser /var/log/xrdp*

WORKDIR /opt

COPY remote/setup_workspace.py /opt/setup_workspace.py
RUN chown techuser /opt

COPY startup.sh startup.sh
RUN chmod +x startup.sh

USER techuser
ENTRYPOINT [ "/home/techuser/startup.sh" ]