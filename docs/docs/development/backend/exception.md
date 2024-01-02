<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Exception Handling

Various errors can occur in the backend, which must be made understandable to
the end user and the developers when calling the API.

In general, please use the following syntax to return a error message from the
backend:

```py title="routes.py"
from fastapi import HTTPException

raise HTTPException(
    status_code=403,  # (1)
    detail={
        "err_code": "project_deletion_permission_denied",  # (2)
        "title": "Permission denied",  # (3)
        "reason": (
            "You don't have the permission to delete projects.",
            "Please ask your administrator to delete the project.",
        ),  # (4)
        "technical": "The role administrator is required.",  # (5)
    },
)
```

## Important Hints for Exceptions

1. Please use the corresponding HTTP response status code here. More
   information about status codes:
   <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>
1. _Optional_: Unique error code (as string). Can be evaluated in the frontend
   to identify a specific error.
1. _Optional_: Use a title that is automatically displayed in the frontend
   (only works when the `reason` parameter is provided).
1. _Optional_: Use a message that is automatically displayed in the frontend
   for users. Since the message will be displayed to end users, it should
   contain context for classification and should be user-friendly (not
   technical!)
1. _Optional_: Technical message for developers, not displayed in the frontend.
   Is part of the error response json.
