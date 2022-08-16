# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 1st party:
from capellacollab.config import config


def get_username(token: t.Dict[str, t.Any]) -> str:
    return token[config["authentication"]["jwt"]["usernameClaim"]].strip()
