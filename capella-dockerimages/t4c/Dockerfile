ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

# Install T4C
COPY ./updateSite /opt/updateSite
WORKDIR /opt/updateSite
## Install T4C Plugins via the P2 API from Eclipse
RUN T4C_ZIP=$(find . -type f -iname "*.zip" | head -n 1 | cut -c 3-); \
    /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository jar:file:///opt/updateSite/$T4C_ZIP!/ \
    -installIU com.thalesgroup.mde.melody.collab.feature.feature.group,com.thalesgroup.mde.melody.collab.maintenance.feature.feature.group,com.thalesgroup.mde.melody.collab.licbranding.feature.feature.group && \
    chown -R techuser /opt/capella/configuration

RUN chown techuser /opt/capella/capella.ini && \
    echo '-DOBEO_LICENSE_SERVER_CONFIGURATION=$T4C_LICENCE_SECRET' >> /opt/capella/capella.ini

WORKDIR /opt
ENV BASE_TYPE=t4c
