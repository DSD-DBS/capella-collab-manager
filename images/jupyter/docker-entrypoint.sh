#!/bin/sh

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

mkdir -p "$NOTEBOOKS_DIR"

jupyter-lab --ip=0.0.0.0 \
    --port=$JUPYTER_PORT \
    --no-browser \
    --ServerApp.authenticate_prometheus=False \
    --ServerApp.base_url="$JUPYTER_BASE_URL" \
    --ServerApp.root_dir="$NOTEBOOKS_DIR"
