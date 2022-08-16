# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import os
import pathlib

# 3rd party:
import yaml

# 1st party:
from capellacollab import config


def test_config_loading():
    os.environ["ENV1_ENV2"] = "testvalue"
    os.environ["EXAMPLE_EXAMPLE2"] = "env"
    yaml_dict = yaml.safe_load(
        (pathlib.Path(__file__).parent / "data" / "example_config.yaml").open()
    )

    cfdict = config.ConfigDict(yaml_dict)

    # Environment variable
    assert cfdict["env1"]["env2"] == "testvalue"

    # YAML has priority over environment variable
    assert cfdict["example"]["example2"] == "yaml"

    # YAML variable
    assert cfdict["example"]["example4"] == "works"

    # YAML list variable
    assert cfdict["example"]["example3"][0]["test"]["test2"] == "test3"

    # YAML list variable
    assert cfdict["example"]["example3"][-1] == "test2"
