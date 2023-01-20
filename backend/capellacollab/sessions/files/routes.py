# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import io
import logging
import tarfile

import requests
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from requests.auth import HTTPBasicAuth

from capellacollab.config import config
from capellacollab.sessions.injectables import get_existing_session
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import OPERATOR
from capellacollab.sessions.schema import FileTree

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/", response_model=FileTree)
def get_files(
    show_hidden: bool, session: DatabaseSession = Depends(get_existing_session)
):
    return requests.get(
        "http://" + session.host + ":8000/api/v1/workspaces/files",
        params={"show_hidden": show_hidden},
        auth=HTTPBasicAuth("", session.rdp_password),
        timeout=config["requests"]["timeout"],
    ).json()


@router.post("/")
def upload_files(
    files: list[UploadFile],
    session: DatabaseSession = Depends(get_existing_session),
):
    tar_bytesio = io.BytesIO()

    with tarfile.TarFile(
        name="upload.tar", mode="w", fileobj=tar_bytesio
    ) as tar:
        size = sum(len(file.file.read()) for file in files)
        if size > 31457280:
            raise HTTPException(
                status_code=413,
                detail={
                    "reason": "The summed file size must not exceed 30MB."
                },
            )

        for file in files:
            file.file.seek(0)
            file.filename = file.filename.replace(" ", "_")
            tar.addfile(
                tar.gettarinfo(arcname=file.filename, fileobj=file.file),
                fileobj=file.file,
            )

    tar_bytesio.seek(0)
    tar_bytes = tar_bytesio.read()

    OPERATOR.upload_files(session.id, tar_bytes)

    return {"message": "Upload successful"}


@router.get("/download", response_class=StreamingResponse)
def download_file(
    filename: str, session: DatabaseSession = Depends(get_existing_session)
) -> StreamingResponse:
    return StreamingResponse(
        OPERATOR.download_file(session.id, filename),
        headers={
            "content-disposition": 'attachment; filename=f"{filename}.zip"',
            "content-type": "application/zip",
        },
    )
