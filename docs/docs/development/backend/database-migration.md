<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Create Database Migration Scripts

To create an upgrade script automatically (this will compare the current
database state with the models):

```sh
alembic revision --autogenerate -m "Commit message"
```
