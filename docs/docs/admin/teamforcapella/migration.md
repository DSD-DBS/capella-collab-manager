<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# How to Migrate a Capella Model to a Higher Version (in TeamForCapella)

!!! warning

    A downgrade of Capella models is not possible.

1.  Open a new persistent session with the old Capella version.
1.  Check that nobody is connected to the remote repository:
    [See who is connected to a TeamForCapella repository](../../user/tools/capella/teamforcapella/connected-users/index.md)
1.  Run a backup pipeline and verify that the latest changes are included in
    the Git repository. If the Git repository is already up-to-date, there will
    be no additional commit. In this case, you should check the status of the
    pipeline run.
1.  Import the model from the TeamForCapella server via the Import wizard from
    TeamForCapella into your local workspace:
    [Import a model from TeamForCapella](../../user/tools/capella/teamforcapella/import/index.md)
1.  If you're still connected to the old Capella repository (`*.team` project
    in the workspace), delete the `*.team` project.
1.  Terminate the session.
1.  Remove existing TeamForCapella to Git backup pipelines in the Collaboration
    Manager and note down if the commit history is included:
    [Remove a (nightly) backup](../../user/projects/models/backups/remove.md)
1.  Add a new repository in the TeamForCapella server with the new Capella
    version via the Capella Collaboration Manager:
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

1.  Export the model to the new TeamForCapella server via the Export wizard
    from TeamForCapella:
    [Export a model to TeamForCapella](../../user/tools/capella/teamforcapella/export/index.md)
1.  If you have CI/CD pipelines in the linked Git repositories which depend on
    a specific Capella version, make sure to update them. For our pipelines it
    might be necessary to update the `CAPELLA_VERSION` environment variable.
1.  Recreate the backup pipeline(s) for the new TeamForCapella server version:
    [Set up a TeamForCapella backup](../../user/projects/models/backups/setup.md).
    Start a pipeline run and verify that the changes are included in the Git
    repository. Verify also that the CI/CD pipelines in the linked Git
    repository are still working (if applicable).
1.  Use the [capella-diff-tools](https://github.com/DSD-DBS/capella-diff-tools)
    and compare the commit after the migration with the commit before the
    migration. Verify that the changes are correct.
1.  Communicate to all users that the model has been migrated to a new version.
    Users have to reimport the repositories in their personal workspace. Share
    the following documentation page with all users:
    [Steps after a Model Migration](../../user/tools/capella/teamforcapella/migration/index.md)
1.  At a later point, when the new repository is stable on the new server:
    [Remove the old TeamForCapella repository from the old server](./repository-management/index.md#remove-a-teamforcapella-repository)
