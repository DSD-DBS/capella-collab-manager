# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import appdirs
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

PRIVATE_KEY: rsa.RSAPrivateKey | None = None
PUBLIC_KEY: rsa.RSAPublicKey | None = None

PRIVATE_KEY_PATH = (
    pathlib.Path(appdirs.user_data_dir("capellacollab")) / "private_key.pem"
)

logger = logging.getLogger(__name__)


def generate_private_key() -> rsa.RSAPrivateKey:
    logger.info(
        "Generating a new private key for session pre-authentication..."
    )
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )


def serialize_private_key(key: rsa.RSAPrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def save_private_key_to_disk(key: rsa.RSAPrivateKey, path: pathlib.Path):
    logger.info(
        "Saving private key for session pre-authentication to %s", path
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(
            serialize_private_key(key),
        )


def load_private_key_from_disk(path: pathlib.Path) -> rsa.RSAPrivateKey | None:
    logger.info(
        "Trying to load private key for session pre-authentication from %s",
        path,
    )

    if not path.exists():
        logger.info("No private key found at %s", path)
        return None

    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    if not isinstance(key, rsa.RSAPrivateKey):
        logger.exception("The loaded private key is not an RSA key.")
        return None

    logger.info(
        "Successfully loaded private key for session pre-authentication from %s",
        path,
    )

    return key


def load_private_key_in_memory(key: rsa.RSAPrivateKey):
    global PRIVATE_KEY  # noqa: PLW0603
    global PUBLIC_KEY  # noqa: PLW0603

    PRIVATE_KEY = key
    PUBLIC_KEY = PRIVATE_KEY.public_key()


def initialize_session_pre_authentication():
    private_key = load_private_key_from_disk(PRIVATE_KEY_PATH)

    if not private_key:
        private_key = generate_private_key()
        save_private_key_to_disk(private_key, PRIVATE_KEY_PATH)

    load_private_key_in_memory(private_key)
