<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

??? question "My Capella crashed. What should I do?"

    Capella can crash for many different reasons. Many issues are issues with
    Eclipse Capella itself, so we try to escalate issues there. Bugs can be
    reported to the Eclipse Capella team directly in the
    [Github repository](https://github.com/eclipse/capella/issues).

    Administrators can see the logs of all sessions to identify the issues
    remotely. However, the session owner can also see the events in the UI.
    In your session, please follow these steps:

    1. Open the Capella search
    1. Search for `Event logs` and click on the following entry:
    1. You should now see the list of events and you can try to find an entry with
       a matching timestamp.

??? question "The clipboard doesn't work anymore."

    This is a known bug with our used `RDP`-server `xrdp`. `xrdp` maintains so
    called `channels`, which are managed by the process `chansrv`. One channel
    is `cliprdr`, which enables the clipboard feature. However, `chansrv`
    doesn't terminate properly on session disconnects and `chansrv` doesn't
    accept new connections. This leads to the fact that the clipboard doesn't
    work anymore after a reconnect. The bug is tracked in the
    [`xrdp` Github repository](https://github.com/neutrinolabs/xrdp/issues/1188)
    and in [our Github repository](https://github.com/DSD-DBS/capella-dockerimages/issues/67).

    The only solution for now: You have to terminate the existing session and
    create a new session to get a working clipboard again.

??? question "My read-only sessions shows 'Modelloading failed'"

    This happens if the loading of one of the models fails.
    Please reach out your project lead. If you are project lead, please check
    the primary Git models with a matching tool version of your project.
    These are used for the `read-only` session. Common mistakes are wrong
    credentials, wrong entrypoints (e.g. with typos) and missing `aird`-files.

    If you have no success, please reach out your administrator. Administrators
    can see the logs of read-only sessions.

??? question "The TeamForCapella password doesn't work"

    Since we have released version 2, users have to use sessions passwords. More
    information can be found [here](./flows/t4c.md).
    If you have been added to a project recently while having a running session,
    please recreate your session to get a valid session password for the models
    of the required project.

<!-- prettier-ignore -->
??? question "I can't use the `Control` key for the secondary/right-click on macOS"

    Please use an external mouse or use the trackpad gesture (click with two
    fingers on the trackpad).

    The sessions run on Linux and the `Control` key can't be mapped properly
    via the remote desktop protocol.
