"""Module handling list, download, upload of files for a session."""

# 3rd party:
import aiofiles
from fastapi import APIRouter, UploadFile
from fastapi.responses import HTMLResponse

# local:
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES

router = APIRouter()


@router.get("/")
async def get_files() -> HTMLResponse:
    """Supply file upload form to test file upload.

    Visit http://localhost:8000/api/v1/sessions/files to test the file upload.

    """
    content = """
<body>
<form action="/api/v1/sessions/99999/files/"
      enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@router.post(
    "/",
    responses=AUTHENTICATION_RESPONSES,
)
async def upload_files(files: list[UploadFile]):
    for file in files:
        try:
            contents = await file.read()
            async with aiofiles.open(file.filename, "wb") as f:
                await f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            await file.close()

    return {"message": f"Successfuly uploaded {[file.filename for file in files]}"}
