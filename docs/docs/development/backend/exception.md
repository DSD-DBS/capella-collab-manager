<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Exception Handling

Various errors can occur in the backend, which must be made understandable to
the end user and the developers when calling the API.

In order to maintain consistency and benefit from automatic exception
registration, define exceptions in a route-specific exceptions.py file in the
following manner:

```py title="exceptions.py"
from fastapi import status
from capellacollab.core import exceptions as core_exceptions

class UserNotFoundError(core_exceptions.BaseError): # (1)
    def __init__(
        self, username: str | None = None, user_id: int | None = None # (2)
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, # (3)
            title="User not found", # (4)
            reason=f"The user '{username or user_id}' doesn't exist.", # (5)
            err_code="USER_NOT_FOUND" # (6)
        )
```

1. Exceptions should be defined as subclasses of BaseError from the core
   exceptions module.
2. Any additional data beyond the required BaseError parameters can be supplied
   when initializing an exception.
3. _Required_: Supply the corresponding HTTP response status code for the
   exception. More information about status codes:
   <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>
4. _Required_: Supply a descriptive title for the exception. This will be
   displayed in the frontend.
5. _Required_: Supply the reason the exception occurred. This will be displayed
   in the frontend. It should contain context for classification and should be
   user-friendly, or contain information on a resolution or next step.
6. _Required_: Supply a unique error code (as string). This can be evaluated in
   the frontend to identify a specific error, or more easily filtered for in
   logs.
