# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=bad-builtin

import pathlib

import deepdiff
import yaml

from . import loader


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


print("Start comparison of configuration files")

config_template = yaml.safe_load(
    (
        pathlib.Path(__file__).parents[2] / "config" / "config_template.yaml"
    ).open()
)

config = loader.load_yaml()

diff = deepdiff.DeepDiff(
    config, config_template, ignore_order=True, report_repetition=True
)

for key, value in (
    diff.get("type_changes", {}) | diff.get("values_changed", {})
).items():
    new_value = value["new_value"]
    print(
        f"{bcolors.OKBLUE}"
        f"Your configuration differs to the template. Key {key} has a different value. Expected value '{new_value}'. If you changed the value on purpose, you can ignore this message."
        f"{bcolors.ENDC}"
    )

for key in diff.get("dictionary_item_removed", {}):
    print(
        f"{bcolors.WARNING}"
        f"Found unknown configuration option {key}!"
        f"{bcolors.ENDC}"
    )

for key in diff.get("dictionary_item_added", ""):
    print(
        f"{bcolors.FAIL}"
        f"Missing configuration option {key}. Please add the key to your configuration file."
        f"{bcolors.ENDC}"
    )

if not diff:
    print("Your configuration file is up to date!")
