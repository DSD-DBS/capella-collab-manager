<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Please follow these steps to request a session:

1. Navigate to the `Workspaces` tab inside the web application.
1. Please select your preferred worspace type.

    !!! Question "Which type should I use?"
        Please have a look at [Session Types](types.md)

1. In case of read-only sessions, you have to select a project. Then, two more fields appear where you can choose the revision (i.e. branch or tag) and either the latest commit or complete commit history of the primary model of this project. Instead of choosing a single branch, it is possible to click the checkbox to mark that all branches should be downloaded.

    !!! note ""
        Choosing all revisions and only the latest commit clones only the latest commits for all branches.

1. Click the `Request session` button.
1. You should see the state of your request. It can take up to 2 minutes, until the required resources can be assigned. In most of the cases this takes under 30 seconds.
1. You should now see a success message. Please click on `Connect to Session`.
1. The session should appear in a new tab and Capella starts automatically.
1. Please follow the instructions (depends on the workflow of your project)
    1. [Git](flows/git.md)
    1. [TeamForCapella](flows/t4c.md)
