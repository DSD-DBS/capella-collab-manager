#!/bin/bash
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd

# Load git model
git clone $GIT_URL /home/techuser/model
git checkout $GIT_REVISION

# Prepare Workspace
echo "Preparing workspace..."
export DISPLAY=:99;
Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp &
/opt/capella/capella -data /workspace > /dev/null || r=$?;
if [[ -n "$r" ]] && [[ "$r" == 158 || "$r" == 0 ]]
then 
    echo "Workspace preparation done.";
else 
    echo "Workspace preparation failed! Please check the EASE logs.";
    exit 1;
fi

# Ensure that Capella is closed.
pkill java
pkill capella

unset GIT_USERNAME;
unset GIT_PASSWORD;
rm /opt/scripts/*;

exec supervisord
