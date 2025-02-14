# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from urllib import parse as urllib_parse

import fastapi
from fastapi import responses

router = fastapi.APIRouter()


@router.get("/grafana{_:path}", include_in_schema=False)
@router.get("/prometheus{_:path}", include_in_schema=False)
def redirect_unauthorized_grafana_requests(request: fastapi.Request):
    path = f"{request.url.path}"
    if request.url.query:
        path += f"?{request.url.query}"

    return responses.RedirectResponse(
        url=f"/auth?auto=true&redirectTo={urllib_parse.quote(path)}"
    )
