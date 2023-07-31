# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from capellacollab.config import config


def get_username(token: dict[str, t.Any], is_bearer: bool = True) -> str:
    if is_bearer:
        return token[config["authentication"]["jwt"]["usernameClaim"]].strip()
    else:
        return token["username"]
