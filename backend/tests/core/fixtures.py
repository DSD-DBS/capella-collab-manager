# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import fastapi
import pytest

from capellacollab.core.logging import injectables as logging_injectables


@pytest.fixture(name="mock_router")
def fixture_mock_router() -> fastapi.FastAPI:
    return fastapi.FastAPI()


@pytest.fixture(name="mock_request_logger")
def fixture_mock_request_logger(mock_router: fastapi.FastAPI):
    logger = logging.LoggerAdapter(logger=logging.getLogger())

    def mock_get_request_logger() -> logging.LoggerAdapter:
        return logger

    mock_router.dependency_overrides[
        logging_injectables.get_request_logger
    ] = mock_get_request_logger

    yield mock_router

    del mock_router.dependency_overrides[
        logging_injectables.get_request_logger
    ]
