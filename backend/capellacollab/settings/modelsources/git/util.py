# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

import requests
from sqlalchemy import orm

from capellacollab.settings.modelsources.git import crud as git_crud

from . import exceptions


def verify_path_prefix(db: orm.Session, path: str):
    if not (git_instances := git_crud.get_git_instances(db)):
        return

    unquoted_path = urllib.parse.unquote(path)
    if resolved_path := requests.Request("GET", unquoted_path).prepare().url:
        for git_instance in git_instances:
            unquoted_git_url = urllib.parse.unquote(git_instance.url)
            resolved_git_url = (
                requests.Request("GET", unquoted_git_url).prepare().url
            )

            if resolved_git_url and resolved_path.startswith(resolved_git_url):
                return

    raise exceptions.InstancePrefixUnmatchedError()
