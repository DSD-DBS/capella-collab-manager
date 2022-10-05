# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.responses import (
    AUTHENTICATION_RESPONSES,
)
from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.t4c import crud
from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CInstance,
    DatabaseT4CSettings,
    PatchT4CInstance,
    T4CInstance,
)
from capellacollab.tools import crud as tools_crud

router = APIRouter()


@router.get(
    "/",
    responses=AUTHENTICATION_RESPONSES,
    response_model=list[T4CInstance],
)
def list_git_settings(
    db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return [
        T4CInstance.from_orm(instance)
        for instance in crud.get_all_t4c_instances(db)
    ]


@router.get(
    "/{id_}",
    responses=AUTHENTICATION_RESPONSES,
    response_model=T4CInstance,
)
def get_t4c_instance(
    id_: int, db: Session = Depends(get_db), token=Depends(JWTBearer())
):
    verify_admin(token, db)
    return T4CInstance.from_orm(crud.get_t4c_instance(id_, db))


@router.post(
    "/",
    responses=AUTHENTICATION_RESPONSES,
    response_model=T4CInstance,
)
def create_t4c_instance(
    body: CreateT4CInstance,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    try:
        version = tools_crud.get_version_by_id(body.version_id, db)
    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The version with id {body.version_id} was not found."
            },
        )

    instance = DatabaseT4CSettings(**body.dict())
    instance.version = version
    return T4CInstance.from_orm(crud.create_t4c_instance(instance, db))


@router.patch(
    "/{id_}",
    responses=AUTHENTICATION_RESPONSES,
    response_model=T4CInstance,
)
def edit_t4c_instance(
    id_: int,
    body: PatchT4CInstance,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    verify_admin(token, db)
    try:
        instance = crud.get_t4c_instance(id_, db)
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={
                "reason": f"The t4c instance with the id {id_} does not exist.",
            },
        )
    for key in body.dict():
        value = body.__getattribute__(key)
        if value:
            instance.__setattr__(key, body.__getattribute__(key))
    return T4CInstance.from_orm(crud.update_t4c_instance(instance, db))
