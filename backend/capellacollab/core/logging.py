# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import random
import string
import typing as t

from fastapi import Depends, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from capellacollab.config import config
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer

LOGGING_LEVEL = config["logging"]["level"]


class AttachTraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        request.state.trace_id = trace_id

        return await call_next(request)


class AttachUserNameMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        username = "not set"
        if token := await JWTBearer(auto_error=False)(request):
            username = get_username(token)

        request.state.user_name = username

        return await call_next(request)


class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        get_logger(request).info("request started")
        response: Response = await call_next(request)
        get_response_logger(request).info(
            "request finished", status_code=response.status_code
        )

        return response


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


class ReqLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return (
            "trace_id={trace_id} method={method} path={path} user={user} client={client} {msg_pref}{msg}".format(
                trace_id=self.extra["trace_id"],
                method=self.extra["method"],
                path=self.extra["path"],
                user=self.extra["user"],
                client=self.extra["client"],
                msg_pref="" if self.extra["chaining"] else "message=",
                msg=msg,
            ),
            kwargs,
        )


class ErrorLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        error_code = kwargs.pop("error_code", self.extra["error_code"])
        return (f"error_code={error_code} message={msg}", kwargs)


class ResLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        status_code = kwargs.pop("status_code", self.extra["status_code"])
        return (f"status_code={status_code} message={msg}", kwargs)


def get_general_logger(name: str, log_leveL=LOGGING_LEVEL) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(log_leveL)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "time=%(asctime)s level=%(levelname)s function=%(funcName)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_general_log_args(
    request: Request, chaining=False
) -> t.Dict[str, t.Any]:
    client = request.client
    return {
        "trace_id": request.state.trace_id,
        "method": request.method,
        "path": request.url.path,
        "user": request.state.user_name,
        "client": client[0] + ":" + str(client[1]) if client else "unknown",
        "chaining": chaining,
    }


def get_logger(request: Request) -> logging.LoggerAdapter:
    return ReqLogAdapter(
        get_general_logger(request.url.path), get_general_log_args(request)
    )


def get_error_code_logger(request: Request) -> logging.LoggerAdapter:
    req_logger = ReqLogAdapter(
        get_general_logger(request.url.path, log_leveL=logging.ERROR),
        get_general_log_args(request, chaining=True),
    )
    return ErrorLogAdapter(
        req_logger, {"error_code": None, "request": request}
    )


def get_response_logger(request: Request) -> logging.LoggerAdapter:
    req_logger = ReqLogAdapter(
        get_general_logger(request.url.path),
        get_general_log_args(request, chaining=True),
    )
    return ResLogAdapter(req_logger, {"status_code": None, "request": request})
