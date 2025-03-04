# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi

from capellacollab.configuration.app import config


class _LogAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs):
        extra: dict = self.extra | kwargs.get("extra", {})

        msg = (
            " ".join([f'{key}="{value}"' for key, value in extra.items()])
            + f' message="{msg}"'
        )
        return (msg, kwargs)


def _get_log_args(request: fastapi.Request) -> dict[str, t.Any]:
    log_args = {}
    if client := request.client:
        log_args["client"] = client.host + ":" + str(client.port)
    if hasattr(request.state, "user_name"):
        log_args["user"] = request.state.user_name
    return log_args | {
        "trace_id": request.state.trace_id,
        "method": request.method,
        "path": request.url.path,
        "query_params": request.url.query,
    }


def get_request_logger(request: fastapi.Request) -> logging.LoggerAdapter:
    logger: logging.Logger = logging.getLogger("capellacollab.request")
    logger.setLevel(config.logging.level)

    return _LogAdapter(logger, _get_log_args(request))
