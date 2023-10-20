<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Update a model to a newer version

<!-- prettier-ignore -->
!!! warning
    Create backups (e.g. in a Git repository) before you start the update process.
    A downgrade of models may not be possible (depends on the tool).

<!-- prettier-ignore -->
!!! info
    If you want to update a Capella model, please follow the Capella specific instructions instead:
    [Update a TeamForCapella based Capella model](../../tools/capella/teamforcapella/update.md)

1. Open a new persistent session with the old version of your tool.
1. Load the model with the old version into your persistent workspace.
1. Close the session.
1. Remove the automatic backup option in the Capella Collaboration Manager,
   we'll rewire it at the end of this tutorial.
1. Create a new session with the new Capella version.
1. Migrate the model in your local workspace.
