# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import os
import typing as t
from urllib.parse import quote, urlsplit

# 3rd party:
import git
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from git import Git
from pydantic import BaseModel
from pyparsing import empty

# 1st party:
from capellacollab.core.authentication.jwt_bearer import JWTBearer


class GitRevisions(BaseModel):
    branches: t.List[str]
    tags: t.List[str]


class GitCredentials(BaseModel):
    url: str
    username: t.Optional[str]
    password: t.Optional[str]


router = APIRouter()


@router.get("/revisions/", response_model=GitRevisions)
def get_references(
    model_slug: str,
    url: str,
    username: t.Optional[str],
    password: t.Optional[str],
    token: JWTBearer = Depends(JWTBearer()),
) -> GitRevisions:

    working_directory = model_slug
    splitted_url = urlsplit(url)
    credentials = (
        quote(username or "", safe="") + ":" + quote(password or "", safe="") + "@"
    )
    git_url = (
        f"{splitted_url.scheme}://{credentials}"
        f"{splitted_url.netloc}{splitted_url.path}"
    )
    remote_refs = GitRevisions(branches=[], tags=[])
    try:
        empty_repo = git.Repo.init(working_directory)
        origin = empty_repo.create_remote("origin", git_url)
        origin.fetch()
    except git.exc.GitCommandError as exc:
        empty_repo.delete_remote("origin")
        raise HTTPException(status_code=422, detail="Wrong credentials") from exc
    remote_refs.branches = [ref.name[7:] for ref in origin.refs]
    remote_refs.tags = [tag.name for tag in empty_repo.tags]
    return remote_refs
