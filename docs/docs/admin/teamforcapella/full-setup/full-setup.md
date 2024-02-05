<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

This tutorial will guide you through the full setup of a new
TeamForCapella-based project in the Collaboration Manager.

1. [Create a new project](../../../user/projects/create.md).
1. [Create a new tool model in the project you created](../../../user/projects/models/create.md),
   select Capella as tool and the version you want to use.
1. [Link the TeamForCapella repository to the new model](../project-integration/project-integration.md)
   if you have not done so already.
1. [Link a Git repository](../../../user/projects/models/create.md#step-31-link-existing-git-repository)
   if you have not done so already. It's required for the backup pipelines as
   well as for the diagram cache and model complexity badge.
1. Make sure that the right version and nature is configured for the tool
   model! If they are not configured properly, you would not see the
   TeamForCapella repository in the later export step.
1. [Spawn a new persistent session](../../../user/sessions/request.md). Select
   Capella as the tool, and select the previously selected tool version.
1. Once Capella is open, create a new empty Capella project or import the
   project that you want to initialize the TeamForCapella repository with.
1. [Export the model to the new TeamForCapella repository](../../../user/tools/capella/teamforcapella/export/export-to-t4c.md).
1. [Set up a backup pipeline](../../../user/projects/models/backups/setup.md).
1. [Set up the model complexity badge](../../../user/projects/models/complexity_badge.md).
1. [Set up the diagram cache](../../../user/projects/models/diagrams/setup_diagram_cache.md)
1. Verify that everything works as expected.
