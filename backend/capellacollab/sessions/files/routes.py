# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import io
import logging
import tarfile

import fastapi
from fastapi import responses, status

from capellacollab.sessions import injectables as sessions_injectables
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators

from . import models

router = fastapi.APIRouter()
log = logging.getLogger(__name__)


@router.get("", response_model=models.FileTree)
def list_files(
    show_hidden: bool,
    session: sessions_models.DatabaseSession = fastapi.Depends(
        sessions_injectables.get_existing_session
    ),
):
    try:
        return operators.get_operator().list_files(
            session.id, "/workspace", show_hidden
        )
    except Exception:
        log.exception("Loading of files for session %s failed", session.id)
        raise fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason": "Loading the files of the session failed. Is the session running?"
            },
        )


@router.post("")
def upload_files(
    files: list[fastapi.UploadFile],
    session: sessions_models.DatabaseSession = fastapi.Depends(
        sessions_injectables.get_existing_session
    ),
):
    tar_bytesio = io.BytesIO()

    with tarfile.TarFile(
        name="upload.tar", mode="w", fileobj=tar_bytesio
    ) as tar:
        size = sum(len(file.file.read()) for file in files)
        if size > 31457280:
            raise fastapi.HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "reason": "The summed file size must not exceed 30MB."
                },
            )

        for file in files:
            file.file.seek(0)

            assert file.filename
            file.filename = file.filename.replace(" ", "_")
            tar.addfile(
                tar.gettarinfo(arcname=file.filename, fileobj=file.file),
                fileobj=file.file,
            )

    tar_bytesio.seek(0)
    tar_bytes = tar_bytesio.read()

    operators.get_operator().upload_files(session.id, tar_bytes)

    return {"message": "Upload successful"}


@router.get("/download", response_class=responses.StreamingResponse)
def download_file(
    filename: str,
    session: sessions_models.DatabaseSession = fastapi.Depends(
        sessions_injectables.get_existing_session
    ),
) -> responses.StreamingResponse:
    return responses.StreamingResponse(
        operators.get_operator().download_file(session.id, filename),
        headers={
            "content-disposition": 'attachment; filename=f"{filename}.zip"',
            "content-type": "application/zip",
        },
    )
