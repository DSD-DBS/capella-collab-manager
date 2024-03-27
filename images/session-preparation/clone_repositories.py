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

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")


@dataclasses.dataclass
class Environment:
    GIT_REPOS_JSON = json.loads(os.getenv("GIT_REPOS_JSON", "[]"))
    CAPELLACOLLAB_SESSION_TYPE = os.getenv("CAPELLACOLLAB_SESSION_TYPE", "READONLY")


class _ProjectDict(t.TypedDict):
    url: str
    revision: str
    depth: int
    entrypoint: str
    username: t.NotRequired[str | None]
    password: t.NotRequired[str | None]
    location: str


def fetch_projects_from_environment() -> list[_ProjectDict]:
    return json.loads(os.getenv("GIT_REPOS_JSON", "[]"))


def clone_git_repository(project: _ProjectDict) -> None:
    log.info("Cloning git repository with url %s", project["url"])

    flags = []

    if revision := project["revision"]:
        flags += ["--single-branch", "--branch", revision]

    git_depth = project["depth"]
    if git_depth != 0:
        flags += ["--depth", str(git_depth)]

    subprocess.run(
        ["git", "clone", project["url"], str(project["location"])] + flags,
        check=True,
        env={
            "GIT_USERNAME": project.get("username", None) or "",
            "GIT_PASSWORD": project.get("password", None) or "",
            "GIT_ASKPASS": os.environ["GIT_ASKPASS"],
        },
    )
    log.info(
        "Clone of git repository with url %s was successful",
        project["url"],
    )


def main():
    projects = fetch_projects_from_environment()
    for project in projects:
        clone_git_repository(project)


if __name__ == "__main__":
    main()
