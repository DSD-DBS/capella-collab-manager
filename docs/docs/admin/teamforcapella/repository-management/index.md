<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# TeamForCapella Repository Management

For all actions, you have to navigate to `Menu` > `Settings` > `TeamForCapella`
(below `Model sources`). Select your instance. On the right side, you should
see a card with the name `Manage T4C repositories`. In this card, you can see
all existing repositories with their status.

## Add a new TeamForCapella Repository

1. Enter the name of the repository in the `Repository name` field.
1. Click on `Add T4C repository`
1. The status should be `INITIAL`. Please wait until the status changes to
   `ONLINE`

## Start/Stop a TeamForCapella Repository

1. Select the repository from the list
1. Click the `Start repository` or `Stop repository` button on the bottom
   right.

## Remove a TeamForCapella Repository

!!! danger

    Deleted TeamForCapella repositories can not be restored.
    If you don't have backups, the models in the repository are not recoverable!

1. Select the repository from the list
1. Click the `Remove <repository-name>` button.
1. Another dialog opens where you have to manually type in the name of the
   repository. Copy&Paste doesn't work here. You have to confirm the deletion.
1. The repository should not appear in the list anymore if the deletion was
   successful.
