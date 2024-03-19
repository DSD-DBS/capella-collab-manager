<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Troubleshooting

!!! question "My Capella crashed. What should I do?"

    Capella can crash for many different reasons. Many issues are issues with
    Eclipse Capella itself, so we try to escalate issues there. Bugs can be
    reported to the Eclipse Capella team directly in the
    [Github repository](https://github.com/eclipse/capella/issues).

    Administrators can see the logs of all sessions to identify the issues
    remotely. In addition, the session owner can also see the events in the UI.
    In your session, please follow these steps:

    1. Open the Capella search
    1. Search for `Event logs` and click on the following entry:
    1. You should now see the list of events and you can try to find an entry with
       a matching timestamp.

!!! question "The description editor doesn't load anymore"

    In some cases the description doesn't load anymore, is just a blank page, or looks like this:

    ![Description Editor](./description-editor.png){:style="width:400px"}

    This is a common and known bug in Capella itself. We have reported it to the Capella contributors,
    but there is no fix available yet. You can track the status on GitHub: <https://github.com/eclipse-capella/capella/issues/2316>

    If you are experiencing this problem, please try one of the following workarounds:

    - Open the description editor by double-clicking the model element you want to edit, and open the description editor from the overlay:
      ![Element overlay](./description-editor-overlay.png)
    - Open the Description Editor from the Properties tab:
      ![Properties tab](./description-editor-properties.png)
    - Reopen Capella in the current session from the task bar at the top of the session window. Expand `File` and close Capella. It will reopen automatically.

        ![Exit Capella](./exit-capella.png)
    - End your session and request a new session in the Capella Collaboration Manager.


    If none of these workarounds help, the only solution is to reset your workspace. Please contact your administrator for assistance.
