# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.tools import models as tools_models
from capellacollab.tools import util as tools_util


def test_additional_ports_are_unique():
    with pytest.raises(ValueError):
        tools_models.HTTPPorts(
            metrics=9118,
            http=8080,
            additional={"restapi": 5007, "restapi2": 5007},
        )


def test_additional_ports_not_reserved_keys():
    with pytest.raises(ValueError):
        tools_models.HTTPPorts(
            metrics=9118,
            http=8080,
            additional={"http": 5007},
        )


def test_additional_port_already_in_use():
    with pytest.raises(ValueError):
        tools_models.HTTPPorts(
            metrics=9118,
            http=8080,
            additional={"restapi": 8080},
        )


def test_additional_ports_reserved_port():
    with pytest.raises(ValueError):
        tools_models.HTTPPorts(
            metrics=9118,
            http=8080,
            additional={"test": 80},
        )


def test_environment_resolution():
    ports = tools_models.HTTPPorts(
        metrics=9118,
        http=8080,
        additional={"restapi": 5007},
    )
    assert tools_util.resolve_tool_ports(ports) == {
        "metrics": 9118,
        "http": 8080,
        "restapi": 5007,
    }
