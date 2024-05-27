# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import collections.abc as cabc
import logging
import os
import pathlib
import subprocess

from . import exceptions, models

log = logging.getLogger(__name__)


async def ls_remote(url: str, env: cabc.Mapping[str, str]) -> list[str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "ls-remote",
            url,
            stdout=asyncio.subprocess.PIPE,
            env=os.environ | env,
        )
    except subprocess.CalledProcessError as e:
        log.debug(
            {
                "msg": "Exit code 128 during ls_remote of the repository "
                + url,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "exitcode": e.returncode,
            }
        )
        if e.returncode == 128:
            raise exceptions.GitRepositoryAccessError()
        else:
            raise e
    stdout, _ = await proc.communicate()
    return stdout.decode().strip().splitlines()


async def get_remote_refs(
    url: str, username: str, password: str, default=None
) -> models.GetRevisionsResponseModel:
    remote_refs: models.GetRevisionsResponseModel = (
        models.GetRevisionsResponseModel(branches=[], tags=[])
    )

    git_env = {
        "GIT_USERNAME": username or "",
        "GIT_PASSWORD": password or "",
        "GIT_ASKPASS": str(
            (pathlib.Path(__file__).parents[0] / "askpass.py").absolute()
        ),
    }
    for ref in await ls_remote(url, git_env):
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
