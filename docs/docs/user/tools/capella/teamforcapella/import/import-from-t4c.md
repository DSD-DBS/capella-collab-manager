<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Import a Capella Model from a TeamForCapella Server into your Persistent Workspace

<!-- prettier-ignore -->
!!! warning
    To import a Capella model into your persistent workspace, you need
    at least the `Read/Write`-permission in the project.

<!-- prettier-ignore -->
!!! info
    This imports a model into your workspace and changes are not automatically saved
    back to the T4C repository. If you want to save changes directly back to the server
    use [this](../../../../sessions/flows/t4c.md) documentation.

1. Open a persistent session with the corresponding Capella version.
1. Wait until Capella has started.
1. Click on `File` > `Import...`. <br />
   ![Capella import dialog](./capella-import-dialog.png)
1. A dialog with the title `Select` should open. In the dialog, expand
   `TeamForCapella`, select `Capella project from remote repository` and
   confirm with `Next`.
   ![Import project from remote repository](./project-from-remote-repository.png)
1. Select the repository from the dropdown menu. Click on the `Test connection`
   button and enter your [session token](../../../../sessions/flows/t4c.md).
   ![Select repository for import](./import-repository-selection.png)
1. Click on `Next` .
   <!-- prettier-ignore -->
    !!! warning
        Do NOT modify the default location. Only the `/workspace` directory is persistent.
        ![Use default location](./use-default-location.png)
   <!-- prettier-ignore -->
    !!! hint
        ![Project already exists in workspace](./project-already-exists-in-workspace.png)
        If you get the message `A project with the same name already exists in your workspace`,
        change the name in the `Local Project Name` field.
        ![Change local project name](./change-local-project-name.png)

1. Select `Import all images` during the next step (step does not exist on
   Capella 5.x.x). ![Import all images](./import-all-images.png)
1. Confirm with `Finish`. You should see a success message:
   ![Imported resources](./imported-resources-message.png)
1. Click on `Ok` and the project should appear in your persistent workspace.
