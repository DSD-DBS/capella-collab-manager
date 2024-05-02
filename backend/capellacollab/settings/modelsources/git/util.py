# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

from capellacollab.settings.modelsources.git import crud as git_crud


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

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "err_code": "NO_GIT_INSTANCE_WITH_PREFIX_FOUND",
            "reason": "We couldn't find a matching Git instance. Make sure that your system administrator allows the given URL.",
            "technical": f"There is no Git instance, which has a prefix of the path '{path}' as URL.",
        },
    )
