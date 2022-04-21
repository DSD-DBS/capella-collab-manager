# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import yaml

options = yaml.safe_load(pathlib.Path("options.yaml").open())

print(int(options["database"]["deploy"]))
