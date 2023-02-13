# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import io
import logging
import tarfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from capellacollab.sessions.injectables import get_existing_session
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.schema import FileTree

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/", response_model=FileTree)
def list_files(
    show_hidden: bool, session: DatabaseSession = Depends(get_existing_session)
):
    try:
        return get_operator().list_files(session.id, "/workspace", show_hidden)
    except Exception:
        log.exception("Loading of files for session %s failed", session.id)
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "Loading the files of the session failed. Is the session running?"
            },
        )


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

    get_operator().upload_files(session.id, tar_bytes)

    return {"message": "Upload successful"}


@router.get("/download", response_class=StreamingResponse)
def download_file(
    filename: str, session: DatabaseSession = Depends(get_existing_session)
) -> StreamingResponse:
    return StreamingResponse(
        get_operator().download_file(session.id, filename),
        headers={
            "content-disposition": 'attachment; filename=f"{filename}.zip"',
            "content-type": "application/zip",
        },
    )
