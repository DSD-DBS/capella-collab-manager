# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json
import pathlib
import subprocess


def run_git_command(cmd: list[str]):
    return subprocess.run(
        ["git", *cmd],
        check=True,
        capture_output=True,
        cwd=pathlib.Path(__file__).parent,
    ).stdout.decode()


(pathlib.Path(__file__).parent / "src" / "assets" / "version.json").write_text(
    json.dumps(
        {
            "git": {
                "version": run_git_command(["describe", "--tags"]).strip(),
                "tag": run_git_command(["describe", "--tags", "--abbrev=0"]).strip(),
            }
        }
    )
)
