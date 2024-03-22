<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

In order to make the whole backend more consistent, it is divided into
different modules. This is to ensure that these can be outsourced without major
impacts and that other modules can be added as "plugins".

A extension has the following structure: <br>

```bash
extension
├── __init__.py
├── crud.py
├── injectables.py
├── models.py
├── routes.py
└── ...
```

The different components are explained in the following section.

## Extension Modules

### `__init__.py`

Code to be called to initialize a module.

### `crud.py`

All `CRUD` (Create, read, update and delete) related operations. They should be
used to access the database. They should be used to access the database, in
case there are no existing injectables.

There should not be much logic in the `crud.py` files (really just creating,
reading, updating and deleting) models in the database.

### `injectables.py`

In the `injectables` module, we define useful functions that allow to retrieve
resources by simply defining the resource as parameter of the fastapi route and
using the injectable function as dependency (i.e.,
`resource: ResourceType = Depends(injectableFunction)`). By using these
injectables, we reduce the code duplication, since we include logic (such as
checking whether a project exists) into the injectable function, and the
readability of the code is increased.

### `models.py`

In the `models` module, all `pydantic` and `SQLAlchemy` models should be
defined. In general, we use the `Database` prefix for `SQLAlchemy` models,
e.g., `DatabaseProject`.

### `routes.py`

The `routes` module should include all fastAPI routes.

### `...`

Other submodules can of course be created and are usually also useful if logic
needs to be implemented.
