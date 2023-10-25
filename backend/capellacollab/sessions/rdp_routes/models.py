# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic


class SessionRoute(pydantic.BaseModel):
    host: str | None
    username: str
    password: str | None
