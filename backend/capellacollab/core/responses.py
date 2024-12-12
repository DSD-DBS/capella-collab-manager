# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import typing as t

import fastapi

from capellacollab import openapi as capellacollab_openapi
from capellacollab.configuration.app import config

from . import exceptions


def translate_exceptions_to_openapi_schema(
    excs: list[type[exceptions.BaseError]],
):
    if capellacollab_openapi.should_skip_openapi_error_responses():
        return {}

    grouped_by_status_code: dict[int, list[exceptions.BaseError]] = {}

    for exc in excs:
        example = exc.openapi_example()
        grouped_by_status_code.setdefault(example.status_code, []).append(
            example
        )

    return {
        status_code: {
            "content": {
                "application/json": {
                    "schema": {
                        "oneOf": [
                            {
                                "$ref": f"#/components/schemas/{exc.__class__.__name__}",
                            }
                            for exc in excs
                        ],
                    }
                }
            },
        }
        for status_code, excs in grouped_by_status_code.items()
    }


def set_secure_cookie(
    response: fastapi.Response,
    key: str,
    value: str,
    path: str,
    expires: datetime.datetime | None = None,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        path=path,
        samesite="strict",
        httponly=True,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )


def delete_secure_cookie(
    response: fastapi.Response, key: str, path: str
) -> None:
    response.delete_cookie(
        key=key,
        path=path,
        samesite="strict",
        httponly=True,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )


class SVGResponse(fastapi.responses.Response):
    """Custom error class for SVG responses.

    To use the class as response class, pass the following parameters
    to the fastapi route definition.

    ```python
    response_class=fastapi.responses.Response
    responses=responses.SVGResponse.responses
    ```

    Don't use SVGResponse as response_class as this will also change the
    media type for all error responses, see:
    https://github.com/tiangolo/fastapi/discussions/6799

    To return an SVG response in the route, use:

    ```python
    return responses.SVGResponse(
        content=b"<svg>...</svg>",
    )
    ```
    """

    media_type = "image/svg+xml"
    responses: dict[int | str, dict[str, t.Any]] | None = {
        200: {
            "content": {
                "image/svg+xml": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        }
    }


class ZIPFileResponse(fastapi.responses.StreamingResponse):
    """Custom error class for zip-file responses.

    To use the class as response class, pass the following parameters
    to the fastapi route definition.

    ```python
    response_class=fastapi.responses.Response
    responses=responses.ZIPFileResponse.responses
    ```

    Don't use ZIPFileResponse as response_class as this will also change the
    media type for all error responses, see:
    https://github.com/tiangolo/fastapi/discussions/6799

    To return an ZIP-file response in the route, use:

    ```python
    return responses.ZIPFileResponse(
        file_generator(),
    )
    ```
    """

    media_type = "application/zip"
    responses: dict[int | str, dict[str, t.Any]] | None = {
        200: {
            "content": {
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        }
    }


class MarkdownResponse(fastapi.responses.Response):
    """Custom error class for Markdown responses.

    To use the class as response class, pass the following parameters
    to the fastapi route definition.

    ```python
    response_class=fastapi.responses.Response
    responses=responses.MarkdownResponse.responses
    ```

    Don't use Markdown as response_class as this will also change the
    media type for all error responses, see:
    https://github.com/tiangolo/fastapi/discussions/6799

    To return an Markdown response in the route, use:

    ```python
    return responses.MarkdownResponse(
        content=b"# Hello World",
    )
    ```
    """

    media_type = "text/markdown"
    responses: dict[int | str, dict[str, t.Any]] | None = {
        200: {"content": {"text/markdown": {"schema": {"type": "string"}}}}
    }
