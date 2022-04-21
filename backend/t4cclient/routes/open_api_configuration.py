AUTHENTICATION_RESPONSES = {
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
                        "detail": "One of the roles '[user, manager, administrator]' in the repository test is required."
                    }
                }
            }
        },
    },
}
