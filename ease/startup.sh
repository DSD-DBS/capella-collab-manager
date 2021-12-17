#!/bin/bash
Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp &
/opt/capella/capella -data $EASE_WORKSPACE || r=$?
if [[ -n "$r" ]] && [[ "$r" == 158 || "$r" == 0 ]]; then exit 0; else exit 1; fi