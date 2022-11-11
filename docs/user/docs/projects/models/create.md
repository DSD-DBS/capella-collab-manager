<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Create a _Collab Manager_ model

Collab Manager proposes a wizard to create models in a project. To create a model, you have to be at least project
manager, and you need to be administrator to add a Team for Capella source, which is needed to set up a Team for Capella
backup. To create a model, go to the _Projects_ tab of the navigation bar, open the project in witch you want to create
a model, and click on the “+” icon.

The creation can be interrupted at any step, however an unfinished model will lack some essential features, so it’s
recommended to go through the whole project.

This wizard is also available in the project creation wizard.

### Create model

This page allows to set a project name and description and a tool. The name and tool are required.

### Choose primary source

On this page, you can select the type of source (Git or Team for Capella) to associate to the model. Note however that
Team for Capella is only available for Capella models, and can only be selected by administrators.

### Add source

#### Git source

The Git source should be a Git repository with write rights.

!!! Warning, the credentials entered will be used to write on the repository. This means that from the repository
perspective, the author will be the user.

!!! Warning, the credentials are stored in the database, and even if not fetchable from the interface, they are stored
in plain text, so the password of the user should not be used. Rather use a token.

!!! Warning, the credentials should only work with the repository and not with others, because changing the repository
while keeping the credentials could give access to another repository on behalf on the credential user. To prevent this
use a repository-level token.

#### T4C source

A T4C Instance has to exist in database, with an available repository. See #TODO

For right managements at a Team for Capella level, although it’s possible to create several sources per repository, it’s
recommended to have only one source per repository.

### Choose initialisation

For now, the only possible initialisation is to create an empty model, with specifying a version and a nature. This is
however only an information for the database, and this will not perform any initialisation.
