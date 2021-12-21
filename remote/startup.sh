#!/bin/bash
set -e
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd;
python3 /opt/setup_workspace.py

exec supervisord