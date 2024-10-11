<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Session Types

The Capella Collaboration Manager offers different Session Types:

## Persistent Sessions

Persistent Sessions will store your work in the `/workspace` folder. Persistent
Sessions allows you to use personal workspace within Capella. By default, we
will request 20GB of storage for your personal workspace.

If your project uses the T4C-workflow, we will suggest all visible models in
the T4C connection dialog.

!!! warning

    Only work stored in the `/workspace` folder (and subdirectories) will
    be persistent. If you store your work in another folder, it will be lost
    when the session is closed.

### Provisioned Sessions

Provisioned Sessions are a special type of Persistent Sessions. They are
available in projects and can be used to initialize a workspace with content
from Git repositories. After the initial provisioning, changes will be saved.
You can reset the state at any time to the latest state of the Git repository.

Provisioned sessions are a good alternative to persistent sessions if you only
have read-only access in a project but want to make changes on the model that
you want to integrate later.

The provisioned workspace will saved in your personal workspace in the folder
`/workspace/{project_slug}/tool-{tool_id}`.

## Read-Only Sessions

Read-Only Sessions allow you to read information from models without the risk
of changing the model. The can be useful if you want to review a model or don't
have permissions to write to the model.

!!! info

    Read-only sessions only work for models with linked Git repositories.

!!! danger

    Any changes made in read-only sessions will NOT be saved and cannot be restored.
