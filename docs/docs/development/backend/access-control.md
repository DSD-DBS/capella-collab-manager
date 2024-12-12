<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Access Control

Routes can be protected with access control.

Access control consists of a resource and a verb. A combination of these two is
called a permission. Those permissions are grouped together into a scope. A
role has access to a scope. There are two different types of scopes: A global
scope and a project scope.

A good overview over all available permissions can be found on the token
creation page (`Menu` > `Tokens` in the frontend). To see which permissions are
needed for a specific route, you can consult the API documentation.

## Protect a route

To protect a route, add a dependency to the route definition. The required
permission will be automatically added to the API documentation.

### Global scope

To protect a project route, add the following dependency to the route
definition:

```py
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        configuration={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ]
)
def example_route():
    ...
```

To access this route, the UPDATE verb of the configuration resource in the
admin group of the global scope is required.

---

To restrict a route to logged in users, but without any required permissions,
use the following dependency:

```py
from capellacollab.permissions import injectables as permissions_injectables

@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(required_scope=None)
        )
    ]
)
def example_route():
    ...
```

### Project scope

To protect a project route, add the following dependency to the route
definition:

```py
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)

@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    root={permissions_models.UserTokenVerb.UPDATE}
                )
            )
        )
    ]
)
def example_route():
    ...
```

To access this route, the UPDATE verb of the root resource in the corresponding
project is required.
