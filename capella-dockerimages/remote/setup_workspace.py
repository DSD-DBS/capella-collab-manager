# Copyright 2021 DB Netz AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import glob
import logging
import os
import pathlib
import re

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("prepare_workspace")

OBEO_COLLAB_CONF = pathlib.Path(
    "/workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/fr.obeo.dsl.viewpoint.collab.prefs"
)
REPOSITORIES_BASE_PATH = pathlib.Path("/opt/capella/configuration")
ECLIPSE_UI_PREFS_PATH = (
    REPOSITORIES_BASE_PATH / ".settings" / "org.eclipse.ui.ide.prefs"
)


def replace_config(path: pathlib.Path, key: str, value: str) -> None:
    """This will replace the existing config or add the config (if it doesn't exist)"""
    path.parent.mkdir(exist_ok=True, parents=True)
    if path.exists():
        file_content = path.read_text()
    else:
        file_content = ""

    pattern = f"{key}=.+"
    match = re.search(pattern, file_content)
    if match:
        LOGGER.info("Set existing config %s to %s", key, value)
        file_content = re.sub(pattern, f"{key}={value}", file_content)
    else:
        file_content += f"\n{key}={value}"

    path.write_text(file_content)


def setup_repositories() -> None:
    t4c_repositories = os.getenv("T4C_REPOSITORIES", "").split(",")
    t4c_host = os.getenv("T4C_SERVER_HOST", "localhost")
    t4c_port = os.getenv("T4C_SERVER_PORT", 2036)

    for repo in t4c_repositories:
        replace_config(
            REPOSITORIES_BASE_PATH
            / "fr.obeo.dsl.viewpoint.collab"
            / "repository.properties",
            repo,
            fr"tcp\://{t4c_host}\:{t4c_port}/{repo}",
        )


if __name__ == "__main__":
    LOGGER.info("Prepare Workspace...")

    # Disable Welcome Screen
    replace_config(ECLIPSE_UI_PREFS_PATH, "showIntro", "false")

    if (
        os.getenv(
            "BASE_TYPE",
            "capella",
        )
        == "t4c"
    ):
        # Set default T4C Server IP address
        replace_config(
            OBEO_COLLAB_CONF,
            "PREF_DEFAULT_REPOSITORY_LOCATION",
            os.getenv("T4C_SERVER_HOST", "localhost"),
        )

        # Set default repositories in selection dialog
        setup_repositories()
