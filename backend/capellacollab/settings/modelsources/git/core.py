# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import collections.abc as cabc
import logging
import os
import pathlib
import subprocess

from fastapi import HTTPException

log = logging.getLogger(__name__)


def ls_remote(url: str, env: cabc.Mapping[str, str]) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-remote", url], capture_output=True, check=True, env=env
        )
    except subprocess.CalledProcessError as e:
        log.debug(
            {
                "msg": "Exit code 128 during cloning of the repository " + url,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "exitcode": e.returncode,
            }
        )
        if e.returncode == 128:
            raise HTTPException(
                status_code=500,
                detail={
                    "err_code": "no_git_model_credentials",
                    "reason": "There was an error accessing the model. Please ask your project lead for more information. In most cases, the credentials need to be updated.",
                },
            )
        else:
            raise e
    return proc.stdout.decode().strip().splitlines()


def get_remote_refs(url: str, username: str, password: str):
    remote_refs: dict[str, list[str]] = {"branches": [], "tags": []}

    git_env = os.environ.copy()
    git_env["GIT_USERNAME"] = username
    git_env["GIT_PASSWORD"] = password
    git_env["GIT_ASKPASS"] = str(
        pathlib.Path(__file__).parents[0] / "askpass.py"
    )

    for ref in ls_remote(url, git_env):
        (_, ref) = ref.split("\t")
        if "^" in ref:
            continue
        if ref.startswith("refs/heads/"):
            remote_refs["branches"].append(ref[len("refs/heads/") :])
        elif ref.startswith("refs/tags/"):
            remote_refs["tags"].append(ref[len("refs/tags/") :])

    log.debug("Determined branches: %s", remote_refs["branches"])
    log.debug("Determined tags: %s", remote_refs["tags"])

    return remote_refs
