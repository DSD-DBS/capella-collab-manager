# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import copy
import json
import os
import pathlib
import typing as t

import typer

app = typer.Typer(help="Generate OpenAPI schema for the API.")


@app.command()
def generate(
    output_file: pathlib.Path,
    # For client generation, default keys might blow up the generated code.
    remove_default_keys: bool = typer.Option(
        default=False,
        help=(
            "Remove default keys from the schema."
            " This might be useful for client generation to reduce verbosity of the generated code."
        ),
    ),
    # Reason for this option is: https://github.com/fastapi/fastapi/issues/240
    remove_min_max_keys: bool = typer.Option(
        default=False,
        help=(
            "Remove the exclusiveMinimum and exclusiveMaximum keys from the schema."
            " This improves compatibility with OpenAPI Spec 3.0."
        ),
    ),
    skip_error_responses: bool = typer.Option(
        default=False,
        help=(
            "Skip generation of error responses."
            " This might be useful for client generation to reduce verbosity of the generated code."
        ),
    ),
    remove_unique_items_keys: bool = typer.Option(
        default=False,
        help=(
            "Remove the uniqueItems keys from the schema."
            " This can be helpful in auto-generated clients to use arrays instead of sets."
        ),
    ),
    remove_security_schemes: bool = typer.Option(
        default=False,
        help=(
            "Remove the securitySchemes and security keys from the schema."
            " This can be helpful in auto-generated clients to skip generation of authentication code."
        ),
    ),
):
    """Generate openapi.json and write it to output_file."""

    if skip_error_responses:
        os.environ["CAPELLACOLLAB_SKIP_OPENAPI_ERROR_RESPONSES"] = "1"

    from capellacollab import __main__

    keys_to_remove = []

    if remove_default_keys:
        keys_to_remove.append("default")

    if remove_min_max_keys:
        keys_to_remove.extend(["exclusiveMinimum", "exclusiveMaximum"])

    if remove_unique_items_keys:
        keys_to_remove.append("uniqueItems")

    if remove_security_schemes:
        keys_to_remove.append("security")
        keys_to_remove.append("securitySchemes")

    schema = __main__.app.openapi()
    _remove_keys_from_spec(schema, keys_to_remove)
    with output_file.open("w") as f:
        json.dump(schema, f)


def _remove_keys_from_spec(value: t.Any, keys_to_remove: list[str]):
    if isinstance(value, dict):
        for k in copy.deepcopy(value):
            if k in keys_to_remove:
                del value[k]
            else:
                _remove_keys_from_spec(value[k], keys_to_remove)
    elif isinstance(value, list):
        for i in value:
            _remove_keys_from_spec(i, keys_to_remove)
