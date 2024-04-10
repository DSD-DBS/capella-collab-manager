<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Manage T4C Instances

## Define a T4C Instance

1.  Please navigate to `Menu` > `Settings`
1.  Select `T4C` bewlow `Model sources`
1.  You can see all existing instances (if any). To add a new instance, click
    on the "Add an instance" card. You have to enter the following information:
    <!-- prettier-ignore -->
    1. **Name**: Any name to identify the instance
    1. **Capella version**: Capella version that corresponds to the instance
    1. **License configuration**: License key of your license server
    1. **Protocol**: Protocol that should be used to communicate between
    capella sessions and the T4C server
    1. **Host**: Hostname of the T4C server
    1. **Port**, **CDO Port**, and **HTTP Port** Corresponding ports of your server
    1. **License server API**: License server API url
    1. **REST API**: REST API URL of the T4C server
    1. **Username**: Username with access to the REST API, required for communication
    with the REST API
    1. **Password**: Password corresponding to username

## Archive a T4C Instance

1.  Please navigate to `Menu` > `Settings`
1.  Select `T4C` bewlow `Model sources`
1.  Click on the instance that you want to archive
1.  Click on the `Archive` button. When everything worked you should see a
    messages stating "Instance updated: The instance _name_ is now archived"

An archived instance can no longer be selected when creating a new T4C model
and is highlighted with a gray background and an `Archived` tag in the bottom
right in the T4C instance overview. Existing linked T4C models and all
repositories corresponding to the archived instance will continue to work as
before.
