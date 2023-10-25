<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Please follow these steps to request a session:

1. Navigate to the `Projects` tab inside the web application, and select your
   project.
1. In the project select a model tool and version in the "Read-only session"
   section. Only tools and versions used in the project are shown.
1. Click the `Request a read-only session` button.
1. A popup will request you to select the models that are compatible with the
   selected tool. Once you select a model, you get the option to select a
   branch.
1. You have an option to create a "deep clone". Normally only the latest
   version of a model is loaded. A deep clone will make all previous revisions
   available. It will take longer to start the session.
1. Click the `Start session` button.
1. You're redirected to the `Sessions` tab.
1. Wait for your read-only session to become ready and open it with the
   `Connect` button.

## Automatic Session Termination

When your session is inactive for a long time (default 90 minutes), your
session is terminated. A session is considered inactive when there is no user
activity with your session, even if you have your session open in the browser.

For read-only sessions this means that you have to start a new session. For
persistent sessions the data is persisted, and you can just request a new
session.
