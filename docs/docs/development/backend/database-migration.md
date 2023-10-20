<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Create database migrations scripts

To create an upgrade script automatically (this will compare the current
database state with the models):

```sh
alembic revision --autogenerate -m "Commit message"
```
