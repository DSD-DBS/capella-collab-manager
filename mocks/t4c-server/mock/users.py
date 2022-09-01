# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger()


class PostUserRequest(BaseModel):
    id: str
    isAdmin: bool
    password: str


@router.post("/")
def add_user(body: PostUserRequest, repositoryName: str):
    logger.info("Added user with body %s.", body)
    return body


@router.delete("/{userName}")
def remove_user(userName: str):
    logger.info("Removed user %s.", userName)
    return {}


@router.put("/{userName}")
def update_user(userName: str):
    logger.info("Updated user %s.")
    return {}
