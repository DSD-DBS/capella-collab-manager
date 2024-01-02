# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from capellacollab.config import config

from . import keystore

# Our "singleton" key store:
KeyStore = keystore._KeyStore(jwks_uri=keystore.get_jwks_uri_for_azure_ad())


cfg = config["authentication"]["azure"]


def get_jwk_cfg(token: str) -> dict[str, t.Any]:
    return {
        "audience": cfg["client"]["id"],
        "key": KeyStore.key_for_token(token).model_dump(),
    }
