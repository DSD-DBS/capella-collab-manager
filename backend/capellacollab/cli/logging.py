# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import rich.logging as rich_logging
import typer


def initialize_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            rich_logging.RichHandler(
                markup=True,
                show_time=False,
            )
        ],
    )


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
