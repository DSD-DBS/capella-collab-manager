# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import secrets
import string


def generate_password(length: int = 10) -> str:
    return "".join(
        secrets.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
