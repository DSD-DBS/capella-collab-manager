<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Connect to a TeamForCapella Repository

!!! info

    Connecting to a T4C model in that way will open a connection and automatically
    write changes back to the T4C model. If you do not want to write changes back you can follow
    [the import T4C model](../import/index.md)
    tutorial

To access a TeamForCapella based model you first need read/write access from a
model lead (usually this role is allocated to lead architects / area owners).

!!! info

    Please [request a persistent session](../../../../sessions/request.md) before you continue
    with the instructions here.

1.  During the session creation, you perhaps already noticed the TeamForCapella
    session token. If you've already closed the dialog, please reopen it by
    clicking `Connect` for your desired session under `Active Sessions`.
    Whenever you create a session, we select all TeamForCapella models with the
    same Capella version that you have access to. For those repositories, we
    create a session token and register it with `TeamForCapella`. The access is
    revoked after session termination. Please copy the session token (you can
    just click on the text to copy it):

    ![Session password](screenshots/session-token.png)

1.  When Capella is finally loaded you navigate to `File` > `New` > `Other`.

    ![Open Connection dialog](screenshots/step_1.png)

1.  Expand `Team for Capella` and select `Capella Connected Project`:

    ![Connect to remote model](screenshots/step_2.png)

1.  In the drop-down select the repository you like to work on. In most cases
    the repository and project name should match.
1.  Click on `Test connection` and enter you username and the session token you
    received in the first step.
    ![Test TeamForCapella connection](screenshots/cap-test-conn.jpg)

    !!! info

         The username in the `Test connection` dialog should be already
         pre-filled, however if this is not the case you may need to fill it in
         manually.

    !!! bug

         Do not make use of the `Remember me` functionality.

1.  When the connection test is completed successfully you can click the `Next`
    button.
1.  Finally a Project selection dialog should appear - the defaults are usually
    good, just click `Finish`. This should result in a new folder
    `project-name.team` in your Project Explorer. Open the project, locate a
    file with a `.aird` extension and double-click it to open the model in
    read-write mode.

    ![Project explorer](screenshots/connection-example.jpg)
