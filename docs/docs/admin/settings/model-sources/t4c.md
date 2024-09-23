<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Manage T4C Instances

To use Team for Capella, you must set up a license server and at least one T4C
instance. To do this, go into the `Settings` section of the Collaboration
Manager and select `T4C` below `Model sources`.

## Define a T4C License Server

You can see all existing license servers (if any). To add a new license server,
click on the "Add a license server" card. You have to enter the following
information:

-   **Name**: Any name to identify the license server
-   **License Server API**: The URL of the license server API
-   **License Key**: License key of your license server

## Define a T4C Instance

You can see all existing instances (if any). To add a new instance, click on
the "Add an instance" card. You have to enter the following information:

-   **Name**: Any name to identify the instance
-   **Capella version**: Capella version that corresponds to the instance
-   **License Server**: Select the license server that should be used for this
    instance
-   **Protocol**: Protocol that should be used to communicate between capella
    sessions and the T4C server
-   **Host**: Hostname of the T4C server
-   **Port**, **CDO Port**, and **HTTP Port** Corresponding ports of your
    server
-   **REST API**: REST API URL of the T4C server
-   **Username**: Username with access to the REST API, required for
    communication with the REST API
-   **Password**: Password corresponding to username

## Archive a T4C Instance

1.  Click on the instance that you want to archive
1.  Click on the `Archive` button. When everything worked you should see a
    messages stating "Instance updated: The instance _name_ is now archived"

An archived instance can no longer be selected when creating a new T4C model
and is highlighted with a gray background and an `Archived` tag in the bottom
right in the T4C instance overview. Existing linked T4C models and all
repositories corresponding to the archived instance will continue to work as
before.
