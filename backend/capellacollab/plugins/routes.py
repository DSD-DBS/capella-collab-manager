# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import typing as t

import fastapi
import requests
import yaml
from requests import auth
from sqlalchemy.orm import Session

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as user_models

from . import crud, injectables, models, schema

logger = logging.getLogger(__name__)
schema_router = fastapi.APIRouter()
router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=user_models.Role.USER
            )
        )
    ]
)


@router.get(
    "",
    response_model=list[models.Plugin],
)
def get_plugins(
    db: Session = fastapi.Depends(database.get_db),
) -> list[models.Plugin]:
    return [
        models.Plugin.model_validate(plugin) for plugin in crud.get_plugins(db)
    ]


@router.get(
    "/{plugin_id}",
    response_model=models.Plugin,
)
def get_plugin_by_id(
    plugin: models.DatabasePlugin = fastapi.Depends(
        injectables.get_existing_plugin
    ),
) -> models.DatabasePlugin:
    return plugin


@router.get(
    "/{plugin_id}/refresh",
    response_model=list[models.Plugin],
)
def refresh_plugins(
    db: Session = fastapi.Depends(database.get_db),
    plugin: models.DatabasePlugin = fastapi.Depends(
        injectables.get_existing_plugin
    ),
):
    plugin.content = fetch_content(
        plugin.remote, plugin.username, plugin.password
    )
    db.commit()


@router.post("/peek-plugin-content", response_model=models.Plugin)
def fetch_plugin_content(plugin: models.CreatePlugin) -> models.Plugin:
    content = fetch_content(plugin.remote, plugin.username, plugin.password)
    return models.Plugin(
        id=0,
        remote=plugin.remote,
        username=plugin.username,
        password=plugin.password,
        content=content,
    )


def fetch_content(
    url: str, username: str | None, password: str | None
) -> dict[str, t.Any]:
    basic_auth = None
    if username and password:
        basic_auth = auth.HTTPBasicAuth(username=username, password=password)

    response = requests.get(url, auth=basic_auth, timeout=2)
    response.raise_for_status()
    return yaml.safe_load(response.content.decode())


@router.patch(
    "/{plugin_id}",
    response_model=models.Plugin,
    tags=["Plugins"],
)
def update_plugin(
    body: models.PatchPlugin,
    plugin: models.DatabasePlugin = fastapi.Depends(
        injectables.get_existing_plugin
    ),
    db: Session = fastapi.Depends(database.get_db),
) -> models.DatabasePlugin:
    content = fetch_content(body.remote, body.username, body.password)
    return crud.update_plugin(db, plugin, body, content)


@router.post(
    "",
    response_model=models.Plugin,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=user_models.Role.ADMIN
            )
        )
    ],
    tags=["Plugins"],
)
def create_plugin(
    body: models.CreatePlugin,
    db: Session = fastapi.Depends(database.get_db),
) -> models.Plugin:
    content = fetch_content(body.remote, body.username, body.password)
    return models.Plugin.model_validate(
        crud.create_plugin(
            db,
            remote=body.remote,
            username=body.username,
            password=body.password,
            content=content,
        )
    )


@router.delete(
    "/{plugin_id}",
    status_code=204,
    tags=["Plugins"],
)
def delete_plugin(
    plugin: models.DatabasePlugin = fastapi.Depends(
        injectables.get_existing_plugin
    ),
    db: Session = fastapi.Depends(database.get_db),
) -> None:
    crud.delete_plugin(db, plugin)


@schema_router.get("")
def get_plugin_schema() -> dict[str, t.Any]:
    return schema.get_plugin_schema()
