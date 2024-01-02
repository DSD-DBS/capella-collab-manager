# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

AUTHENTICATION_RESPONSES: dict[str | int, dict[str, t.Any]] = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "detail": {
                            "err_code": "token_exp",
                            "reason": "The Signature of the token is expired. Please request a new access token or refresh the token.",
                        }
                    }
                }
            }
        },
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "detail": {
                            "reason": {
                                "One of the roles '[user, manager, administrator]' in the project test is required."
                            }
                        }
                    }
                }
            }
        },
    },
}
