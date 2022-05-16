# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class PostServerRequest(BaseModel):
    id: str
    isAdmin: bool
    password: str


@router.post("/")
def add_user(body: PostServerRequest, repositoryName: str):
    print(body)
    return body


@router.delete("/{userName}")
def remove_user():
    return {}


@router.put("/{userName}")
def update_user():
    return {}
