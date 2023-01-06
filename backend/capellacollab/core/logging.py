# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

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


class MakeTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename: str | os.PathLike[str]):
        pathlib.Path(filename).parent.mkdir(exist_ok=True)
        super().__init__(filename, when="D", backupCount=1, delay=True)


class AttachTraceIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        request.state.trace_id = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
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
            logging.getLogger(request.url.path).exception(
                msg=f'traceId={request.state.trace_id} message="{exc}"',
                exc_info=True,
            )
            raise exc


class LogRequestsMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: base.RequestResponseEndpoint
    ):
        get_logger(request).debug("request started")
        response: Response = await call_next(request)
        get_logger(request).debug(
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


def get_general_logger(name: str, log_leveL=LOGGING_LEVEL) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    logger.addFilter(HealthcheckFilter())
    logger.setLevel(log_leveL)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            'time="%(asctime)s" level=%(levelname)s function=%(funcName)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_log_args(request: Request) -> t.Dict[str, t.Any]:
    log_args = {}
    if client := request.client:
        log_args["client"] = client.host + ":" + str(client.port)
    return log_args | {
        "trace_id": request.state.trace_id,
        "method": request.method,
        "path": request.url.path,
        "user": request.state.user_name,
    }


def get_logger(request: Request) -> logging.LoggerAdapter:
    return LogAdapter(
        get_general_logger(request.url.path), get_log_args(request)
    )
