FROM base

ENV DEBIAN_FRONTEND=noninteractive

# Install WebKit with GTK
COPY libs /tmp/libs
RUN if [ "$INJECT_PACKAGES" == "true" ]; then \
    # Inject old packages manually
    apt-get install -y $(find /tmp/libs -iname "*.deb") && \
    rm -r /tmp/libs; \
    else \
    # Download old packages from the Ubuntu focal registry
    ## Add source
    echo "deb http://de.archive.ubuntu.com/ubuntu/ focal main" >> /etc/apt/sources.list && \
    ## Import the required keys
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C && \
    apt-get update && \
    ## Install the packages
    apt-get install -y \
    libjavascriptcoregtk-4.0-18=2.28.1-1 \
    libwebkit2gtk-4.0-37=2.28.1-1 && \
    rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR /opt/

COPY ./archives/capella.* /opt/
RUN if [ -s capella.zip ]; then \
    # Install Capella using zip
    unzip capella.zip -d . && \
    rm capella.zip; \
    # Install Capella using tar.gz
    elif [ -s capella.tar.gz ]; then \ 
    tar -xf capella.tar.gz; \
    else \
    echo "capella.zip and capella.tar.gz are empty! Please add you custom Capella zip or tar.gz" && \
    exit 1; \
    fi && \
    rm -rf samples capella.zip capella.tar.gz

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

ENV BASE_TYPE=capella