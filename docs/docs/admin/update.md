<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Update the Collaboration Manager

## Update to a newer version

1. [Create a backup of the backend database](./backup-recovery.md#create-backup)
   before updating.
1. Check the
   [Release Notes](https://github.com/DSD-DBS/capella-collab-manager/releases){:target="\_blank"}
   for any breaking changes or special instructions.
1. Either download the helm chart from the GitHub Releases or check-out the
   revision of the version you'd like to update to:

    ```zsh
    git checkout ${VERSION:?}
    ```

1. Upgrade the Helm Chart, either by using the downloaded chart:

    ```zsh
    helm upgrade \
        --dependency-update \
        -f values.yaml \
        ${RELEASE_NAME:?} \
        collab-manager-${VERSION:?}$.tgz
    ```

    or using the local Git repository:

    ```zsh
    helm upgrade \
        --dependency-update \
        -f values.yaml \
        ${RELEASE_NAME:?} \
        ./helm
    ```

1. Wait until all containers are up & running. If a container can't be started
   anymore, check the logs of the container for more information or
   [roll-back the update](#roll-back-to-a-previous-version).

## Roll-back to a previous version

1.  Find out if there were any database migrations between the current version
    and the version you'd like to roll-back to.

    You can do so with the
    [GitHub Compare](https://github.com/DSD-DBS/capella-collab-manager/compare)
    feature. Select the current version and the version you'd like to roll-back
    and check for any changes in the `backend/capellacollab/alembic` directory.

    If there are no changes, skip the next steps and run the update as usual.

1.  Scale down the backend deployment to 0:

    ```zsh
    kubectl scale deployment ${RELEASE_NAME:?}-backend --replicas=0
    ```

1.  Restore the backup of the backend database to the state it was before the
    update as described in the
    [restore documentation](./backup-recovery.md#restore-backup).

    !!! danger

        This will discard any changes made to the database after the update.

1.  Run the update as usual and use the version you'd like to roll-back to as
    target version.
