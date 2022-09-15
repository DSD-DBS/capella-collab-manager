# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.config import config

from .keystore import KeyStore

cfg = config["authentication"]["oauth"]


def get_jwk_cfg(token: str) -> dict[str, any]:
    return {
        "algorithms": ["RS256"],
        "audience": cfg["audience"] or cfg["client"]["id"],
        "key": KeyStore.key_for_token(token).dict(),
    }
