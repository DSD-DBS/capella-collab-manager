<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Projects are self-managed. There are different roles for this:

<table markdown="span">
    <tr>
        <th>Role</th>
        <th>Permissions</th>
    </tr>
    <tr>
        <td>`Global Administrator`</td>
        <td>
            :material-check-all: All permissions <br>
            :material-check: Manage TeamForCapella instances <br>
            :material-check: Manage TeamForCapella repositories <br>
            :material-check: Manage Git repositories</td>
    </tr>
    <tr>
        <td>`Project administrator`</td>
        <td>
            :material-check: Manage users of a project <br>
            :material-check: Manage model sources <br>
            :material-check: Manage backup jobs <br>
            :material-check: `Read` and `Write` access to linked models <br>
            :material-check: Manage linked models <br>
            :material-close: Link an existing Git repository <br>
            :material-close: Link an existing TeamForCapella repository <br>
            :material-close: Delete models
    </tr>
    <tr>
        <td>`User`/`Read/Write`</td>
        <td>
            :material-check: `Read` and `Write` access to linked models <br>
            :material-check: Access to linked TeamForCapella repositories
    </tr>
    <tr>
        <td>`User`/`Read only`</td>
        <td>
            :material-check: `Read only` access to linked models
    </tr>
    <tr>
        <td>`User` without project access</td>
        <td>
            :material-check: Start persistent sessions
    </tr>
</table>
