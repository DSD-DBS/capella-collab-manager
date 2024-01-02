# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import subprocess
import typing as t


def run_git_command(cmd: list[str]):
    return subprocess.run(
        ["git", *cmd],
        check=True,
        capture_output=True,
        cwd=pathlib.Path(__file__).parent,
    ).stdout.decode()


(pathlib.Path(__file__).parent / ".git_archival.txt").write_text(
    f"node: {run_git_command(['log', '-1', '--format=%H'])}"
    f"node-date: {run_git_command(['log', '-1', '--format=%cI'])}"
    f"describe-name: {run_git_command(['describe', '--tags', '--long'])}"
    f"ref-names: {run_git_command(['log', '-1', '--format=%D'])}",
    encoding="ascii",
)
