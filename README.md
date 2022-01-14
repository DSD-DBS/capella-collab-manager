# Installation

## Requirements
The following tools have to be installed and have to be present in your `PATH`: 
- `kubectl` (Installed and configured for the target cluster/namespace)
- `helm` 
- `python3`
- `docker` (only if you'd like to deploy the database automatically in the cluster)

## Setup databases

### Guacamole Database: 
If you like to run your databases in the k8s cluster, please set `database.deploy: True` in the `options.yaml`. Everything is handled automatically then.

Guacamole supports the following database types: 

- MySQL
- PostgreSQL

To initialize the database, you have to run one of the following commands:

For PostgreSQL:
```
docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --postgres > initdb.sql
```

and for MySQL:
```
docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --mysql > initdb.sql
```

Please update the database with the the resulting SQL script. 
If you run your database in a docker container (`postgres` or `mysql`), you can easily mount the `initdb.sql` file to the `docker-entrypoint-initdb.d` directory inside the container. It will then be executed automatically on startup.

### T4C Manager Database: 
The T4C Manager supports all SQLAlchemy compatible databases.
It has been only tested with PostgreSQL, thus we highly recommend using PostgreSQL.
The backend comes with an automatic database version management and thus all tables are created and migrated automatically.

## Configuration

You have to set the variables according to the descriptions in the `options.yaml` and `values.yaml`.
The `options.yaml` contains all application specific variables, the `values.yaml` all Kubernetes specific variables. 

## Deployment 

For the first deployment, please run: 
```
./commands/install.sh
```

When you'd like to update configuration variables or like to upgrade to a newer version, please run: 
```
./commands/upgrade.sh
```