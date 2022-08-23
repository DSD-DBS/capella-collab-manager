# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import io
import logging
import tarfile

import requests

# 3rd party:
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session

from t4cclient.config import config

# local:
from t4cclient.core.authentication.database import (
    check_session_belongs_to_user,
)
from t4cclient.core.authentication.helper import get_username
from t4cclient.core.authentication.jwt_bearer import JWTBearer
from t4cclient.core.database import get_db
from t4cclient.core.oauth.responses import AUTHENTICATION_RESPONSES
from t4cclient.sessions.database import get_session_by_id
from t4cclient.sessions.operators import OPERATOR
from t4cclient.sessions.schema import FileTree

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/", response_model=FileTree)
def get_files(
    id: str,
    show_hidden: bool,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    check_session_belongs_to_user(get_username(token), id, db)
    session = get_session_by_id(db, id)

    return requests.get(
        "http://" + session.host + ":8000/api/v1/workspaces/files",
        params={"show_hidden": show_hidden},
        auth=HTTPBasicAuth("", session.rdp_password),
        timeout=config["requests"]["timeout"],
    ).json()


@router.post(
    "/",
    responses=AUTHENTICATION_RESPONSES,
)
def upload_files(
    id: str,
    files: list[UploadFile],
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
):
    check_session_belongs_to_user(get_username(token), id, db)

    tar_bytesio = io.BytesIO()
    tar = tarfile.TarFile(name="upload.tar", mode="w", fileobj=tar_bytesio)

    size = sum([len(file.file.read()) for file in files])
    if size > 31457280:
        raise HTTPException(
            status_code=413,
            detail="The summed file size must not exceed 30MB.",
        )

    for file in files:
        file.file.seek(0)
        file.filename = file.filename.replace(" ", "_")
        tar.addfile(
            tar.gettarinfo(arcname=file.filename, fileobj=file.file),
            fileobj=file.file,
        )

    tar.close()
    tar_bytesio.seek(0)
    tar_bytes = tar_bytesio.read()

    OPERATOR.upload_files(id, tar_bytes)

    return {"message": "Upload successful"}


@router.get(
    "/download",
    responses=AUTHENTICATION_RESPONSES,
)
def download_file(
    id: str,
    filename: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> UploadFile:
    check_session_belongs_to_user(get_username(token), id, db)

    tar_bytes = OPERATOR.download_file(id, filename)

    with open(filename, "wb") as f:
        f.write(tar_bytes)

    return UploadFile(filename=filename, file=tar_bytes)
