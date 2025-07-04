# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typer

from capellacollab.core import logging as core_logging

from . import keys, openapi, scheduler, ws

core_logging.initialize_logging(filename="cli.log")

app = typer.Typer()
app.add_typer(ws.app, name="ws")
app.add_typer(openapi.app, name="openapi")
app.add_typer(keys.app, name="keys")
app.add_typer(scheduler.app, name="scheduler")

if __name__ == "__main__":
    app()
