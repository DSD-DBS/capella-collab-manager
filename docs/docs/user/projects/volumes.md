<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Project Volumes

Project volumes provide a limited workspace for sharing files between members
of a project. They are mounted into all sessions of the project members.

## Manage a Volume

Project administrators can create and delete volumes in a project.

## Access a Volume

Volumes are mounted into all sessions of the project members. You can access
the volume under `/shared/<project-slug>`.

The permissions are derived with the following rules:

**Persistent sessions without provisioning:**

All shared volumes of projects are mounted according to the user's or token's
permission. If `shared_volumes:update` (read-write user) is granted, the volume
is mounted read-write. If `shared_volumes:get` (read-only user) is granted, the
volume is mounted read-only. Otherwise, the volume is not mounted.

**Persistent session with provisioning:**

Same as persistent sessions without provisioning, but only projects that are
part of the provisioning are considered.

**Read-only sessions:**

Same as persistent sessions with provisioning, but all volumes are mounted as
read-only.
