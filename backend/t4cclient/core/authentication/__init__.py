# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from importlib import metadata

from t4cclient.config import config


def get_authentication_entrypoint():
    try:
        ep = next(
            i
            for i in metadata.entry_points()["capellacollab.authentication.providers"]
            if i.name == config["authentication"]["provider"]
        )
        return ep
    except StopIteration:
        raise ValueError(
            "Unknown authentication provider " + config["authentication"]["provider"]
        ) from None
