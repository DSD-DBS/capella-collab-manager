<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!-- prettier-ignore-start -->

1. Please navigate to your <a href="/" target="_blank">Active Sessions</a>
1. Find your session, select `Terminate` and confirm your decision.
1. We'll send a signal to the used tool (e.g. Capella) to properly terminate.
   The tool has 60 seconds to terminate, otherwise the process is force killed.

    !!! abstract "Technical background"
        When a user clicks the `Terminate session` button, a `SIGTERM` is sent
        to the container. The container reacts to the signal and terminates the
        tool as well as other used programs (e.g. the `xrdp` server). After a
        grace period of 60 seconds, the container recevies a `SIGKILL`,
        which results in a force-kill.

!!! danger
    All unsaved work is lost and cannot be restored after closing a session.

!!! info
    If you close Capella in the session manually, it will automatically restart.
    Please terminate sessions via the application context (like described above).

<!-- prettier-ignore-end -->
