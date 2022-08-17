# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from t4cclient.config import config


def get_username(token: t.Dict[str, t.Any]) -> str:
    return token[config["authentication"]["jwt"]["usernameClaim"]].strip()
