# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def add_user():
    return {}


@router.delete("/{userName}")
def remove_user():
    return {}


@router.put("/{userName}")
def update_user():
    return {}
