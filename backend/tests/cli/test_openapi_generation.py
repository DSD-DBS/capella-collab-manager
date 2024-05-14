# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

from capellacollab.cli import openapi


def test_openapi_generation(tmp_path: pathlib.Path):
    path = tmp_path / "openapi.json"
    openapi.generate(path)
    assert path.exists()
