# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.Tag],
    tags=["Tags"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(required_scope=None)
        )
    ],
)
def get_tags(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.DatabaseTag]:
    """Get all available tags."""
    return crud.get_all_tags(db=db)


@router.put(
    "/{tag_id}",
    response_model=models.Tag,
    tags=["Tags"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tags={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            )
        )
    ],
)
def update_tag(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    existing_tag: t.Annotated[
        models.DatabaseTag,
        fastapi.Depends(injectables.get_existing_tag_by_id),
    ],
    body: models.CreateTag,
) -> models.DatabaseTag:
    """Update a tag, including all references in projects."""
    for tag in crud.get_all_tags(db):
        if tag.name == body.name and tag.id != existing_tag.id:
            raise exceptions.TagAlreadyExistsError(tag_name=body.name)
    return crud.update_tag(db, existing_tag, body)


@router.post(
    "",
    response_model=models.Tag,
    tags=["Tags"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tags={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            )
        )
    ],
)
def create_tag(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    body: models.CreateTag,
) -> models.DatabaseTag:
    """Create a new tag."""
    for tag in crud.get_all_tags(db):
        if tag.name == body.name:
            raise exceptions.TagAlreadyExistsError(tag_name=body.name)
    return crud.create_tag(db, body)


@router.delete(
    "/{tag_id}",
    status_code=204,
    tags=["Tags"],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tags={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            )
        )
    ],
)
def delete_tag(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    tag: t.Annotated[
        models.DatabaseTag,
        fastapi.Depends(injectables.get_existing_tag_by_id),
    ],
) -> None:
    """Delete a tag and remove all references from projects."""
    crud.delete_tag(db, tag)
