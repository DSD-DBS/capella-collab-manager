<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Collaboration with Jupyter Notebooks

Collaborating on Jupyter notebooks is a common requirement in various
workflows. This guide describes two main approaches to collaboration:
individual sessions and project-level collaboration.

## Collaboration in Individual Sessions

If you have a notebook in your personal workspace and another user wants to
connect to your sessions, follow these steps:

### Sharing a Notebook Session

1. **Request a Jupyter Session**: As usual, request a Jupyter session to start.
2. **Connect to the Session**: Open the requested session.
3. **Share the Session**: Click on the "Share" button on the top right of the
   Jupyter session interface.
4. **Include the Token**: Tick the option "Include the token in the URL".
5. **Warning! Security Risk**: Be aware that anyone with access to the URL can
   access your Jupyter session until termination. To revoke access, terminate
   your session in the Capella Collaboration Manager. After restarting it, a
   new token will be generated, and old sessions will no longer have access.
6. **Share the Link**: Distribute the link to all users who should have access.
   They will be able to open your notebooks and concurrently edit them.

#### Instructional Video

Here's a video that visually guides you through these steps:

<video controls>
  <source src="../jupyter-collaboration.mp4" type="video/mp4">
</video>

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
   Jupyter sessions to `/workspace/notebooks/<project-slug>/<model-slug>`.
   You'll see it in the Jupyter file explorer under
   `<project-slug>/<model-slug>`.

### Delete Project Notebook Share

To delete the share, remove the model from the project. **Warning!** This
action will irrevocably delete all notebooks in the dedicated workspace!
