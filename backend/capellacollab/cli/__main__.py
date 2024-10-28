# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typer

from . import keys, openapi, ws

app = typer.Typer()
app.add_typer(ws.app, name="ws")
app.add_typer(openapi.app, name="openapi")
app.add_typer(keys.app, name="keys")

if __name__ == "__main__":
    app()
