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


def fetch_projects_from_environment() -> list[_ProjectDict]:
    return json.loads(environment.GIT_REPOS_JSON)


def clone_git_repository(project: _ProjectDict) -> None:
    log.info("Cloning git repository with url %s", project["url"])

    flags = []

    if revision := project["revision"]:
        flags += ["--single-branch", "--branch", revision]

    git_depth = project["depth"]
    if git_depth != 0:
        flags += ["--depth", str(git_depth)]

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
    projects = fetch_projects_from_environment()
    for project in projects:
        clone_git_repository(project)
    log.info("Finished preparation of session")
    log.info("---FINISH_PREPARE_WORKSPACE---")


if __name__ == "__main__":
    main()
