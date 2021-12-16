FROM base

ENV DEBIAN_FRONTEND=noninteractive

# Install WebKit with GTK
COPY libs /tmp/libs
RUN apt-get install -y $(find /tmp/libs -iname "*.deb") && \
    rm -r /tmp/libs

WORKDIR /opt/

# Install Capella using ZIP
COPY ./capella.zip /opt/capella.zip
RUN unzip capella.zip -d . && \
    rm capella.zip && \
    rm -r samples

# Set Permissions
RUN chmod +x capella/capella && \
    chmod -R +x capella/jre/bin && \
    chmod -R +x capella/jre/lib

# Install Dropins for Capella
COPY ./dropins /opt/capella/dropins

# Eclipse settings
RUN mkdir -p /opt/capella/configuration/.settings; \
    ## Do not show WORKSPACE_SELECTION_DIALOG
    echo "SHOW_WORKSPACE_SELECTION_DIALOG=false" >> /opt/capella/configuration/.settings/org.eclipse.ui.ide.prefs; \
    # Setup workspace
    mkdir /workspace; \
    ## Disable Welcome Screen
    mkdir -p /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chown -R techuser /opt/capella/configuration