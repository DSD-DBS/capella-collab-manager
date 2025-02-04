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

class UserNotFoundError(core_exceptions.BaseError): # (1)!
    def __init__(
        self, username: str | None = None, user_id: int | None = None # (2)!
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, # (3)!
            title="User not found", # (4)!
            reason=f"The user '{username or user_id}' doesn't exist.", # (5)!
            err_code="USER_NOT_FOUND" # (6)!
        )

    @classmethod
    def openapi_example(cls) -> "UserNotFoundError":  # (7)!
        return cls("john_doe", -1)
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
7. _Required_: Implement the `openapi_example` class method to provide an
   example of the exception in the OpenAPI documentation.

## OpenAPI Examples

To make exceptions visible as response in the OpenAPI documentation, you can
either reference the exception in the route or a dependency used by the
function.

To reference an exception in a route, add it the `responses` attribute:

```py title="routes.py"
from capellacollab.core import responses

from . import exceptions

@router.get(
    "",
    response_model=str,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.UserNotFoundError,
        ]
    ),
)
def example_route():
    ...
```

To reference an exception in a dependency, define it as attribute:

```py title="injectables.py"
import dataclasses

from . import exceptions

@dataclasses.dataclass(eq=False)
class UserInjectable:
    exceptions = [exceptions.UserNotFoundError]

    def __call__(self,) -> None:
        ...
```
