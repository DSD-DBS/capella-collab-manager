# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from capellacollab.sessions import util


def test_stringify_environment_variables(logger: logging.LoggerAdapter):
    environment = {
        "key1": "value1",
        "key2": 2,
        "key3": {"key4": "value4"},
    }

    warnings = util.stringify_environment_variables(logger, environment)

    assert not warnings
    assert environment == {
        "key1": "value1",
        "key2": "2",
        "key3": '{"key4": "value4"}',
    }


def test_stringify_environment_variables_error(logger: logging.LoggerAdapter):
    class NonSerializableObject:
        pass

    environment = {
        "key1": "value1",
        "key2": 2,
        "key3": NonSerializableObject(),
    }

    warnings = util.stringify_environment_variables(logger, environment)

    assert len(warnings) == 1
    assert warnings[0].err_code == "ENVIRONMENT_DUMPING_FAILED"
    assert environment == {
        "key1": "value1",
        "key2": "2",
    }
