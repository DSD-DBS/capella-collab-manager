# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import logging.handlers
import os
import pathlib
import random
import string
import typing as t

from fastapi import Request, Response
from starlette.middleware import base

from capellacollab.config import config
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer

LOGGING_LEVEL = config["logging"]["level"]


class CustomFormatter(logging.Formatter):
    def __init__(self):
        self._request_formatters = logging.Formatter(
            'time="%(asctime)s" level=%(levelname)s function=%(funcName)s %(message)s'
        )
        self._default_formatter = logging.Formatter(
            'time="%(asctime)s" level=%(levelname)s name=%(name)s function=%(funcName)s message="%(message)s"'
        )
        super().__init__()

    def format(self, record):
        if record.name == "capellacollab.request":
            return self._request_formatters.format(record)

        return self._default_formatter.format(record)


class CustomTimedRotatingFileHandler(
    logging.handlers.TimedRotatingFileHandler
):
    def __init__(self, filename: str | os.PathLike):
        pathlib.Path(filename).parent.mkdir(exist_ok=True)
        super().__init__(filename, when="D", backupCount=1, delay=True)


class AttachTraceIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        request.state.trace_id = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )

        return await call_next(request)


class AttachUserNameMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        username = "anonymous"
        if token := await JWTBearer(auto_error=False)(request):
            username = get_username(token)

        request.state.user_name = username

        return await call_next(request)


class LogExceptionMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        try:
            return await call_next(request)
        except Exception as exc:
            get_request_logger(request).exception(msg=exc, exc_info=True)
            raise


class LogRequestsMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        get_request_logger(request).debug("request started")
        response: Response = await call_next(request)
        get_request_logger(request).debug(
            "request finished", {"status_code": response.status_code}
        )

        return response


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


class LogAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs):
        extra: dict = self.extra | kwargs.get("extra", {})

        msg = (
            " ".join([f'{key}="{value}"' for key, value in extra.items()])
            + f' message="{msg}"'
        )
        return (msg, kwargs)


def _get_log_args(request: Request) -> dict[str, t.Any]:
    log_args = {}
    if client := request.client:
        log_args["client"] = client.host + ":" + str(client.port)
    return log_args | {
        "trace_id": request.state.trace_id,
        "method": request.method,
        "path": request.url.path,
        "user": request.state.user_name,
    }


def get_request_logger(request: Request) -> logging.LoggerAdapter:
    logger: logging.Logger = logging.getLogger("capellacollab.request")
    logger.addFilter(HealthcheckFilter())
    logger.setLevel(LOGGING_LEVEL)

    return LogAdapter(logger, _get_log_args(request))
