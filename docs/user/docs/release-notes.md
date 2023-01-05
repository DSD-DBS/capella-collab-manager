<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## v2.0.0

With version 2.0.0 we create the basis for many new changes and a further
development of the platform. In general, you can view more details in the
corresponding sections of the documentation.

### General tool support

With the new version, we removed some dependencies from Capella. We can now
offer general tool and version support. This means that new tools like
[Papyrus](https://www.eclipse.org/papyrus/) can be easily integrated. Multiple
version support allows users to work on models with different versions. Before,
we had only support for one Capella version at a time.

### Projects as a new central resource

Projects are now in the center of the platform. Every user can create a new
project in a guided process and start working the preferred tools. This allows
the combination of different tools in one project and workflow. In addition, it
adds support for Capella libraries.

### TeamForCapella integration

The TeamForCapella integration has been reworked and has additional features.
Administrators can now add a TeamForCapella instance in the settings.
Repositories can be created with one click and we implemented additional error
handling.

### Improved stability for read-only sessions

Read-only sessions are much more stable and faster. In addition, they do
support multiple models (including libraries) and entrypoints now (you can load
a model from any subdirectory of the linked Git repository).

### Reworked backups

The backup flow has been reworked completely. Project Managers can now trigger
the backup with one click. More configuration options have been added: For each
run, it can be selected if the commit history should be included. Also, project
leads can create templates which can be used for manual triggering.
