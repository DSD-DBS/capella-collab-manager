# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import pytest
from cryptography.hazmat.primitives import serialization

from capellacollab.cli import keys
from capellacollab.sessions import auth as sessions_auth


@pytest.fixture(name="private_key_path")
def fixture_private_key_path(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> pathlib.Path:
    path = tmp_path / "private_key.pem"
    monkeypatch.setattr(sessions_auth, "PRIVATE_KEY_PATH", path)
    return path


def test_key_import(tmp_path: pathlib.Path, private_key_path: pathlib.Path):
    private_key = sessions_auth.generate_private_key()
    path_to_import_from = tmp_path / "private_key_to_import.pem"
    sessions_auth.save_private_key_to_disk(
        private_key, tmp_path / path_to_import_from
    )

    keys.import_private_key(tmp_path / path_to_import_from)

    loaded_key = sessions_auth.load_private_key_from_disk(private_key_path)
    assert loaded_key

    assert sessions_auth.serialize_private_key(
        loaded_key
    ) == sessions_auth.serialize_private_key(private_key)


def test_private_key_export(private_key_path: pathlib.Path):
    private_key = sessions_auth.generate_private_key()
    sessions_auth.save_private_key_to_disk(private_key, private_key_path)

    path_to_export_to = private_key_path.parent / "exported_private_key.pem"
    keys.export_private_key(path_to_export_to, keys.KeyType.PRIVATE)
    loaded_key = sessions_auth.load_private_key_from_disk(path_to_export_to)
    assert loaded_key
    assert sessions_auth.serialize_private_key(
        loaded_key
    ) == sessions_auth.serialize_private_key(private_key)


def test_public_key_export(private_key_path: pathlib.Path):
    private_key = sessions_auth.generate_private_key()
    sessions_auth.save_private_key_to_disk(private_key, private_key_path)

    path_to_export_to = private_key_path.parent / "exported_key.pub"
    keys.export_private_key(path_to_export_to, keys.KeyType.PUBLIC)
    with open(path_to_export_to, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
        )
    assert public_key == private_key.public_key()
