# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import pathlib

import typer

app = typer.Typer(help="Generate OpenAPI schema for the API.")


@app.command()
def generate(
    output_file: pathlib.Path,
):
    """Generate openapi.json and write it to output_file."""

    from capellacollab import __main__

    with output_file.open("w") as f:
        json.dump(__main__.app.openapi(), f)
