# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.settings.modelsources.t4c.injectables import (
    get_existing_instance,
)
from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories import crud
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)


def get_existing_instance_repository(
    t4c_repository_id: t.Optional[int] = None,
    db: Session = Depends(get_db),
    instance: t.Optional[DatabaseT4CInstance] = Depends(get_existing_instance),
) -> t.Optional[DatabaseT4CRepository]:
    if not t4c_repository_id:
        return None
    if not instance:
        raise HTTPException(
            400,
            detail={
                "reason": "Parameters contain a repository id but no instance id."
            },
        )
    try:
        repository = crud.get_t4c_repository(t4c_repository_id, db)
    except NoResultFound as e:
        raise HTTPException(
            404,
            {
                "reason": f"Repository with id {t4c_repository_id} was not found."
            },
        ) from e
    if repository.instance != instance:
        raise HTTPException(
            409,
            {
                "reason": f"Repository {repository.name} is not part of the instance {instance.name}."
            },
        )
    return repository
