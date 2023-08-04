<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Collaboration with Jupyter Notebooks

Collaborating on Jupyter notebooks is a common requirement in various
workflows. This guide describes the approach of collaboration in individual
sessions.

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
