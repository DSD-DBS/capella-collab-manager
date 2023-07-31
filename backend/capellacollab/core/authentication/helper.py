# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from fastapi import security

from capellacollab.config import config


def get_username(token: dict[str, t.Any]) -> str:
    print(token)
    try:
        return token[config["authentication"]["jwt"]["usernameClaim"]].strip()
    except:
        return token.username
