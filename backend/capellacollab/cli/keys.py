# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import pathlib

import typer

from capellacollab.sessions import auth as sessions_auth

app = typer.Typer(
    help="Import and export RSA keys used for session pre-authentication."
)


@app.command(name="import")
def import_private_key(file: pathlib.Path):
    """Read and load a private key from a file.

    After importing the key, it will be used to sign the JWT session tokens.
    The previous key will be discarded.

    Please note that we can only accept private keys which have
    been exported using the `export` command of this CLI.
    """

    key = sessions_auth.load_private_key_from_disk(file)
    if key is None:
        raise typer.BadParameter(
            "The provided file does not contain a valid RSA private key."
        )

    sessions_auth.save_private_key_to_disk(key, sessions_auth.PRIVATE_KEY_PATH)
    sessions_auth.load_private_key_in_memory(key)


class KeyType(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


@app.command(name="export")
def export_private_key(
    file: pathlib.Path, type: KeyType = typer.Option(default=KeyType.PRIVATE)
):
    """Export the current private or public key to a file.

    The private key will be exported in PEM format.
    """

    private_key = sessions_auth.load_private_key_from_disk(
        sessions_auth.PRIVATE_KEY_PATH
    )
    if private_key is None:
        raise typer.BadParameter(
            "No private key has been loaded. Use the `import` command to load a key"
            " or start the backend once to auto-generate a key."
        )

    if type == KeyType.PRIVATE:
        sessions_auth.save_private_key_to_disk(private_key, file)
    else:
        with open(file, "wb") as f:
            f.write(
                private_key.public_key().public_bytes(
                    encoding=sessions_auth.serialization.Encoding.PEM,
                    format=sessions_auth.serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
