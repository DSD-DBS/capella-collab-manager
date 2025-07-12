# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import typer


def verbose_callback(
    *,
    verbose: bool,
) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


VerboseOption = t.Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        envvar="VERBOSE",
        help="Enable verbose output",
        callback=verbose_callback,
    ),
]
