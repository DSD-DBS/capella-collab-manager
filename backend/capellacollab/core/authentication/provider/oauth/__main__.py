# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from capellacollab.config import config

from .keystore import KeyStore

cfg = config["authentication"]["oauth"]


def get_jwk_cfg(token: str) -> dict[str, t.Any]:
    return {
        "algorithms": ["RS256"],
        "audience": cfg["audience"] or cfg["client"]["id"],
        "key": KeyStore.key_for_token(token).model_dump(),
    }
