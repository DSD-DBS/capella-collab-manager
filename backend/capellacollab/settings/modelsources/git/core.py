# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import collections.abc as cabc
import logging
import os
import pathlib
import subprocess

import fastapi
from fastapi import status

from . import models

log = logging.getLogger(__name__)


def ls_remote(url: str, env: cabc.Mapping[str, str]) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-remote", url],
            capture_output=True,
            check=True,
            env=os.environ | env,
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
            raise fastapi.HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "err_code": "no_git_model_credentials",
                    "reason": "There was an error accessing the model. Please ask your project lead for more information. In most cases, the credentials need to be updated.",
                },
            )
        else:
            raise e
    return proc.stdout.decode().strip().splitlines()


def get_remote_refs(
    url: str, username: str, password: str, default=None
) -> models.GetRevisionsResponseModel:
    remote_refs: models.GetRevisionsResponseModel = (
        models.GetRevisionsResponseModel(branches=[], tags=[])
    )

    git_env = {
        "GIT_USERNAME": username or "",
        "GIT_PASSWORD": password or "",
        "GIT_ASKPASS": str(pathlib.Path(__file__).parents[0] / "askpass.py"),
    }
    for ref in ls_remote(url, git_env):
        (_, ref) = ref.split("\t")
        if "^" in ref:
            continue
        if ref.startswith("refs/heads/"):
            remote_refs.branches.append(ref[len("refs/heads/") :])
        elif ref.startswith("refs/tags/"):
            remote_refs.tags.append(ref[len("refs/tags/") :])

    log.debug("Determined branches: %s", remote_refs.branches)
    log.debug("Determined tags: %s", remote_refs.tags)

    if default:
        remote_refs.default = default
        log.debug("Determined default branch: %s", default)

    return remote_refs
