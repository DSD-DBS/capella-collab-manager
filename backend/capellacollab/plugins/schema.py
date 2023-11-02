# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import io
import json
import pathlib
import tempfile
import typing as t

import fastapi
from fastapi import staticfiles
from json_schema_for_humans import generate as json_schema

from . import models

documentation_directory = tempfile.TemporaryDirectory()
documentation_path = pathlib.Path(documentation_directory.name)


def get_plugin_schema_as_json() -> str:
    return json.dumps(get_plugin_schema())


def get_plugin_schema() -> dict[str, t.Any]:
    return models.PluginContent.model_json_schema()


def generate_schema_documentation():
    with tempfile.NamedTemporaryFile(
        mode="w+", encoding="utf-8"
    ) as schema_file:
        schema_file.write(get_plugin_schema_as_json())
        schema_file.seek(0)
        json_schema.generate_from_filename(
            schema_file.name,
            result_file_name=str(documentation_path / "index.html"),
        )


def mount_schema_documentation(app: fastapi.FastAPI):
    app.mount(
        "/docs/plugin-schema",
        staticfiles.StaticFiles(directory=documentation_path, html=True),
        name="plugin-schema-docs",
    )


def cleanup_documentation_directory():
    documentation_directory.cleanup()
