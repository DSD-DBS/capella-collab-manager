# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Due to a bug in the OpenAPI generator,
default keys break the generation of some types.

To fix it, we remove the default keys from the OpenAPI schema.
"""

import copy
import json
import pathlib

PATH_TO_OPENAPI_SCHEMA = pathlib.Path("/tmp/openapi.json")


def remove_default_keys(value: dict):
    if isinstance(value, dict):
        for k in copy.deepcopy(value):
            if k == "default":
                del value[k]
            else:
                remove_default_keys(value[k])
    elif isinstance(value, list):
        for i in value:
            remove_default_keys(i)


if __name__ == "__main__":
    schema = json.loads(PATH_TO_OPENAPI_SCHEMA.read_text())
    remove_default_keys(schema)
    PATH_TO_OPENAPI_SCHEMA.write_text(json.dumps(schema))
