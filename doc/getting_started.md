# Getting started

This guide describes the steps to get started with the Capella Collaboration Manager.

Before you start, make sure you have a running environment. For instructions on how to set up such an environment, please refer to the [README](../README.md).

First open a browser and go to http://localhost:8080.

You will be welcomed by a friendly screen and you can log in. The default setup is running an OAuth mock service for authentication.

![Welcome screen](img/collab-step-1.png)

As username, provide the e-mail address you entered when deploying the cluster. If you forgot to set an e-mail address, use `me@example.com`.

![OAuth mock](img/collab-step-2.png)

You'll be returned to the Collaboration manager. Now you can start a session. Select _Persistent Workspace_ and hit _Request Session_.

![Logged in](img/collab-step-3.png)

The system will now schedule and start a fresh workspace.
Wait a bit for the workspace to be available 

![Starting a session](img/collab-step-4.png)

Once the session is ready, click _Connect to Session_ and a new tab should open. After a few seconds you should see the
Capella splash screen and a workspace will be shown in your browser.

![Capella welcome screen](img/collab-step-5.png)


## What's next

This introduction only scratches the surface of what's possible with the Collaboration Manager.

More advanced features include:

* Read-only models from Git
* Connect to a Team4Capella server (commercial product)
* Manage users and user access
