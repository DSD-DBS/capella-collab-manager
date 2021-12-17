#!/bin/bash
set -e
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd;
python /opt/setup_workspace.py
rm /opt/setup_workspace.py

supervisord