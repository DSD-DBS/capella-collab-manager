#!/bin/bash
# Install deployment for the first time

# Halt the script on error
set -e

# Parse options.yaml to determine to find out if the database should be initialized
python -m venv .venv --system-site-packages --upgrade-deps
source .venv/bin/activate
pip install PyYAML

DEPLOY_DB=$(python3 commands/parse_yaml.py)

if [[ $DEPLOY_DB -eq 1 ]]
then 
    docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --postgres > config/initdb.sql
fi

# Install the helm chart
helm install t4c-access \
    --dry-run \
    -f options.yaml \
    -f values.yaml \
    .