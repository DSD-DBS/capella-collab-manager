<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Projects are self-managed. There are different roles for this:

<!-- prettier-ignore-start -->

| Role                | Permissions |
|||
| `Administrator`     | :material-check-all: All permissions <br> :material-check: Manage TeamForCapella instances <br> :material-check: Manage TeamForCapella repositories <br> :material-check: Manage Git repositories |
| `Project lead`   | :material-check: Manage users of a project <br> :material-check: Manage model sources <br> :material-check: Manage backup jobs <br> :material-check: `Read` and `Write` access to linked models <br> :material-check: Manage linked models <br> :material-close: Link an existing Git repository <br> :material-close: Link an existing TeamForCapella repository <br> :material-close: Delete models  |
| `User`/`Read/Write` | :material-check: `Read` and `Write` access to linked models <br> :material-check: Access to linked TeamForCapella repositories |
| `User`/`Read only`  | :material-check: `Read only` access to linked models
| `User` without project access | :material-check: Start persistent sessions

<!-- prettier-ignore-end -->
