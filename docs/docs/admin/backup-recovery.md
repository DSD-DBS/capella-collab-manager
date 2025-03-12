<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Backup and Recovery Concept

The backup- and restore concept covers 3 components:

- Backend database backups
- Backups of personal workspaces
- Backups of project volumes

## Backend database backups

### Create backup

If the Postgres database is hosted in the Kubernetes cluster, you can create a
backup with:

```zsh
kubectl exec -it deployment/${RELEASE_NAME:?}-backend-postgres -- pg_dump -U backend > backend-dump.sql
```

### Restore backup

```zsh
cat backend-dump.sql | kubectl exec -i deployment/${RELEASE_NAME:?}-backend-postgres -- psql -U backend
```

## Backup of personal workspaces and project volumes

It's recommended to store models in Git or TeamForCapella unless you have an
automated backup strategy for personal workspaces and project volumes.

Personal workspace can be backed up and restored via the CLI. The backups are
not created automatically.

### Create backup

Install the command line tool as described in the
[installation instructions](./cli.md). Verify the installation by executing:

```
python -m capellacollab.cli --help
```

Make sure that your `kubectl` configuration points to the correct cluster.

Run the following command to get a list of all personal workspaces or project
volumes:

```zsh
python -m capellacollab.cli ws volumes
```

Find the name of the workspace you want to backup, then run the following
command:

```zsh
python -m capellacollab.cli ws backup "${VOLUME_NAME:?}"
```

This will produce two files, a `.tar.gz` and a `.json` side-car file. Make sure
to keep both files as the side-car contains important information about the
volume.

### Restore backup

Install the command line tool as described in the
[installation instructions](./cli.md). Verify the installation by executing:

```zsh
python -m capellacollab.cli --help
```

Set up kubectl and point it to the correct cluster. Find the name of the
workspace you want to backup, then run the following command:

```zsh
python -m capellacollab.cli ws backup "${VOLUME_NAME:?}" "${TARFILE:?}"--storage-class-name "${STORAGE_CLASS_NAME:?}"
```
