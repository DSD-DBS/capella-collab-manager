<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Collaboration with Jupyter Notebooks

## Collaboration on Project Level

If you need a shared workspace for notebooks at the project level, you can
create a shared space accessible by all project members.

### Permissions

- **Read/Write Permission**: Allows users to edit the notebook files.
- **Read-only Permission**: Grants view-only access to the Jupyter notebooks.

### Create Project Notebook Share

1. **Create a Model**: In the project, select the tool "Jupyter" and create a
   model. A dedicated workspace will be created automatically. During model
   creation, you don't have to link any sources or repositories.
2. **Access the Workspace**: The workspace is mounted into all newly created
   Jupyter sessions to `/shared/<project-slug>/<model-slug>`. You'll see it in
   the Jupyter file explorer under `shared/<project-slug>/<model-slug>`.

### Delete Project Notebook Share

To delete the share, remove the model from the project. **Warning!** This
action will irrevocably delete all notebooks in the dedicated workspace!
