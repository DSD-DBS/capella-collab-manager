# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib
import random
import string
import time
from logging import handlers as logging_handlers

import fastapi
import rich.logging as rich_logging
from starlette.middleware import base

from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables

from . import injectables


def initialize_logging(filename: str = "backend.log"):
    stream_handler = rich_logging.RichHandler(
        markup=True,
        show_time=False,
    )

    timed_rotating_file_handler = CustomTimedRotatingFileHandler(
        str(config.logging.log_path) + filename
    )
    timed_rotating_file_handler.setFormatter(LogFmtFormatter())

    handlers = [stream_handler, timed_rotating_file_handler]
    logging.basicConfig(
        level=config.logging.level,
        format="%(message)s",
        handlers=handlers,
    )

    # Disable the access logger to avoid duplicate logs
    logging.getLogger("uvicorn.access").disabled = True

    # Change loggers to use the custom handlers
    logging.getLogger("uvicorn").propagate = False

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.propagate = False
    uvicorn_error_logger.handlers = handlers

    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    logging.getLogger("kubernetes.client.rest").setLevel(logging.INFO)


class LogFmtFormatter(logging.Formatter):
    def format(self, record):
        log_format = 'time="%(asctime)s" level=%(levelname)s '
        if record.name == "capellacollab.request":
            log_format += "function=%(funcName)s %(message)s"
        else:
            log_format += (
                'name=%(name)s function=%(funcName)s message="%(message)s"'
            )

        formatter = logging.Formatter(
            log_format, datefmt="%Y-%m-%dT%H:%M:%S%z"
        )

        return formatter.format(record)


class CustomTimedRotatingFileHandler(
    logging_handlers.TimedRotatingFileHandler
):
    def __init__(self, filename: str | os.PathLike):
        pathlib.Path(filename).parent.mkdir(exist_ok=True)
        super().__init__(filename, when="D", backupCount=1, delay=True)


class AttachTraceIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: fastapi.Request, call_next: base.RequestResponseEndpoint
    ):
        request.state.trace_id = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )

        return await call_next(request)


class AttachUserNameMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: fastapi.Request,
        call_next: base.RequestResponseEndpoint,
    ):
        try:
            with database.SessionLocal() as session:
                (
                    user,
                    _,
                ) = await auth_injectables.authentication_information_validation(
                    request, session, injectables.get_request_logger(request)
                )
            username = user.name
        except fastapi.HTTPException:
            username = "anonymous"

        request.state.user_name = username

        return await call_next(request)


class LogExceptionMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: fastapi.Request, call_next: base.RequestResponseEndpoint
    ):
        try:
            return await call_next(request)
        except Exception as exc:
            injectables.get_request_logger(request).exception(
                msg=exc, exc_info=True
            )
            raise


class LogRequestsMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: fastapi.Request, call_next: base.RequestResponseEndpoint
    ):
        started_at = time.perf_counter()
        is_health_check_route = request.url.path == "/healthcheck"
        if not is_health_check_route:
            injectables.get_request_logger(request).debug("request started")
        response: fastapi.Response = await call_next(request)
        if not is_health_check_route:
            injectables.get_request_logger(request).debug(
                "request finished",
                extra={
                    "status_code": response.status_code,
                    "duration": f"{(time.perf_counter() - started_at):.4f}",
                },
            )

        return response
