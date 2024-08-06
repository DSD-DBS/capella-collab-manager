<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->
<!-- prettier-ignore -->
>? QUESTION: **My session window doesn't scale properly** If you use a direct
> session connection via Guacamole, the window doesn't scale automatically
> after browser resizing. You can manually trigger a resize by pressing the
> "Refresh" button in your browser.
>
> Alternatively, you can use our internal session viewer, which comes with
> automatic scaling out of the box.

<!-- prettier-ignore -->
>? QUESTION: **The session requests takes a long time** If a session takes a
> few minutes to start, it means that you've reached a new node that doesn't
> have the requested tool installed (for load balancing reasons, we distribute
> the sessions across different servers). This can happen after updates on our
> end (e.g. when the tool configuration or dependencies are updated) or updates
> from the cluster operator. In both cases, we pull a new Docker image (which
> can be understood as a reinstallation of the tool) on demand.

<!-- prettier-ignore -->
>? QUESTION: **I've minimized my window in Xpra and can't get it back** Just
> refresh the page in the browser. The window should appear again.

<!-- prettier-ignore -->
>? QUESTION: **The clipboard doesn't work anymore.** This is a known bug with our
> used `RDP`-server `xrdp`. `xrdp` maintains so called `channels`, which are
> managed by the process `chansrv`. One channel is `cliprdr`, which enables the
> clipboard feature. However, `chansrv` doesn't terminate properly on session
> disconnects and `chansrv` doesn't accept new connections. This leads to the
> fact that the clipboard doesn't work anymore after a reconnect. The bug is
> tracked in the
> [`xrdp` Github repository](https://github.com/neutrinolabs/xrdp/issues/1188)
> and in
> [our Github repository](https://github.com/DSD-DBS/capella-dockerimages/issues/67).
>
> The only solution for now: You have to terminate the existing session and
> create a new session to get a working clipboard again.

<!-- prettier-ignore -->
>? QUESTION: **My read-only sessions shows 'Modelloading failed'** This
> happens if the loading of one of the models fails. Please reach out your
> project lead. If you are project lead, please check the primary Git models
> with a matching tool version of your project. These are used for the
> `read-only` session. Common mistakes are wrong credentials, wrong entrypoints
> (e.g. with typos) and missing `aird`-files.
>
> If you have no success, please reach out your administrator. Administrators
> can see the logs of read-only sessions.

<!-- prettier-ignore -->
>? QUESTION: **The TeamForCapella password doesn't work** Since we have released
> version 2, users have to use sessions passwords. More information can be found
> [here](../tools/capella/teamforcapella/connect/index.md). If you have been
> added to a project recently while having a running session, please recreate
> your session to get a valid session password for the models of the required
> project.

<!-- prettier-ignore -->
>? QUESTION: **I can't use the `Control` key for the secondary/right-click on
> macOS**
>
> Please use an external mouse or use the trackpad gesture (click with two
> fingers on the trackpad).
>
> The sessions run on Linux and the `Control` key can't be mapped properly via
> the remote desktop protocol.
