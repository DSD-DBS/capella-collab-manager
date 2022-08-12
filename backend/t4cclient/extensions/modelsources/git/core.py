# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import collections.abc as cabc
import logging
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
    return proc.stdout.decode("ascii").strip().splitlines()
