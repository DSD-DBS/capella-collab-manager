#!/bin/bash
set -e
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd;
python3 /opt/setup_workspace.py;

# Replace environment variables in capella.ini, e.g. licences
envsubst < /opt/capella/capella.ini | tee /opt/capella/capella.ini;

exec supervisord
