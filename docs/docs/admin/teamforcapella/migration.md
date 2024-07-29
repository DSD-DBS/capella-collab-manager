<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# How to Update a Capella Model to a Higher Version (in TeamForCapella)

!!! warning

    Please create backups (e.g., in a Git repository) before you start the update process.
    A downgrade of Capella models is not possible.

1.  Open a new persistent session with the old Capella version.
1.  Import the model from the TeamForCapella server via the Import wizard from
    TeamForCapella into your local workspace:
    [Import a model from TeamForCapella](../../user/tools/capella/teamforcapella/import/index.md)
1.  Terminate the session.
1.  Remove existing backups from TeamForCapella:
    [Remove a (nightly) backup](../../user/projects/models/backups/remove.md)
1.  Add a new repository in the TeamForCapella settings:
    [Add a new TeamForCapella repository](./repository-management/index.md#add-a-new-teamforcapella-repository)
1.  Unlink the old TeamForCapella repository (old Capella version) from your
    model:
    [Unlink a TeamForCapella repository](./project-integration/index.md#unlink-a-teamforcapella-repository-from-a-project-model)
1.  Link the new TeamForCapella repository (new Capella version) to your model:
    [Link a TeamForCapella repository](./project-integration/index.md#link-a-teamforcapella-repository-to-a-project-model)
1.  Update the model version to the newer Capella version:
    [Change model metadata](../../user/projects/models/metadata.md)
1.  Create a new session with the new Capella version.
1.  In your persistent workspace, execute the following steps:

    1. Right click on the model in your workspace.
    1. Select `Migration` and `Migrate Project toward current version`
       ![Migrate Capella model](../../user/tools/capella/migration/migrate-capella-model.png)
    1. A backup is not required as the latest version should still be available
       on the old TeamForCapella server.
       ![Disable backup option](../../user/tools/capella/migration/backup-migration.png)

1.  Export the model to the new TeamForCapella server via the Export wizzard
    from TeamForCapella:
    [Export a model to TeamForCapella](../../user/tools/capella/teamforcapella/export/index.md)
1.  Recreate the backup pipeline:
    [Set up a TeamForCapella backup](../../user/projects/models/backups/setup.md)
