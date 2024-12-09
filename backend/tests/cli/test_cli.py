# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from typer import testing

from capellacollab.cli import __main__ as cli


@pytest.fixture(name="cli_runner")
def fixture_cli_runner() -> testing.CliRunner:
    return testing.CliRunner()


def test_cli_help(cli_runner: testing.CliRunner):
    result = cli_runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0

    assert "Usage:" in result.output

    assert "keys" in result.output
    assert "openapi" in result.output
    assert "ws" in result.output
