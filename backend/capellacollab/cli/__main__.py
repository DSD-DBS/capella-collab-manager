# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typer

import capellacollab.cli.ws

app = typer.Typer()
app.add_typer(capellacollab.cli.ws.app, name="ws")

if __name__ == "__main__":
    app()
