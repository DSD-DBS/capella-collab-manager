# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""
This module is executed as standalone script and can't reference or import
other modules from the `capellacollab` project!
"""

import dataclasses
import json
import logging
import os
import pathlib
import shutil
import subprocess
import typing as t


@dataclasses.dataclass
class Environment:
    GIT_REPOS_JSON = os.getenv("CAPELLACOLLAB_PROVISIONING", "[]")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


environment = Environment()


logging.basicConfig(level=environment.LOG_LEVEL)
log = logging.getLogger(__name__)


class _ProjectDict(t.TypedDict):
    url: str
    revision: str
    depth: int

    username: t.NotRequired[str | None]
    password: t.NotRequired[str | None]
    path: str


def _fetch_projects_from_environment() -> list[_ProjectDict]:
    return json.loads(environment.GIT_REPOS_JSON)


def _backup_directory_if_exists(path: pathlib.Path) -> None:
    if not path.exists():
        return

    log.info("Backing up existing directory %s", path)
    backup_path = path.with_name(f"{path.name}.bak")

    if backup_path.exists():
        log.info("Removing existing backup directory %s", backup_path)
        shutil.rmtree(backup_path)
        log.info("Removed existing backup directory %s", backup_path)

    path.rename(backup_path)
    log.info("Backed up existing directory %s to %s", path, backup_path)


def _clone_git_repository(project: _ProjectDict) -> None:
    log.info("Cloning git repository with url %s", project["url"])

    flags = []

    git_depth = project["depth"]
    revision = project["revision"]

    if git_depth != 0:
        flags += ["--depth", str(git_depth)]
        if revision:
            flags += ["--single-branch", "--branch", revision]

    try:
        subprocess.run(
            ["git", "clone", project["url"], str(project["path"])] + flags,
            check=True,
            env={
                "GIT_USERNAME": project.get("username", None) or "",
                "GIT_PASSWORD": project.get("password", None) or "",
                "GIT_ASKPASS": "/etc/git_askpass.py",
            },
        )
        if git_depth == 0 and revision:
            subprocess.run(
                ["git", "-c", "advice.detachedHead=false", "checkout", revision],
                check=True,
                cwd=project["path"],
            )

    except subprocess.CalledProcessError as e:
        log.info("---FAILURE_PREPARE_WORKSPACE---")
        log.error(
            "Clone of git repository with url %s failed with exit code %d",
            project["url"],
            e.returncode,
        )
        raise

    log.info(
        "Successfully cloned Git repository with url '%s' to '%s'",
        project["url"],
        project["path"],
    )


def main():
    log.info("Starting preparation of session")
    log.info("---START_PREPARE_WORKSPACE---")
    projects = _fetch_projects_from_environment()
    for project in projects:
        _backup_directory_if_exists(pathlib.Path(project["path"]))
        _clone_git_repository(project)
    log.info("Finished preparation of session")
    log.info("---FINISH_PREPARE_WORKSPACE---")


if __name__ == "__main__":
    main()
