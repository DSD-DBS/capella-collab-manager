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

### Production

Create a namespaces to deploy the manager and sessions in:

```
helm upgrade --install --create-namespace prod-t4c-manager --namespace prod-t4c-manager -f options.prod.yaml -f values.yaml .
```

## Local development

To develop locally, you can use [K3D](https://k3d.io).

Set up a K8s environmena, a registry and a cluster:

```bash
k3d registry create myregistry.localhost --port 12345    
k3d cluster create ertms --registry-use k3d-myregistry.localhost:12345 --api-port 0.0.0.0:6550 --no-lb
```

Build the services and push them to the cluster registry:

```
docker build -t k3d-myregistry.localhost:12345/t4c/client/backend:latest .
docker push k3d-myregistry.localhost:12345/t4c/client/backend:latest      
```

Repeat for `t4c/client/frontend` (and Capella container?).

* Create an admin token to allow the T4C-manager-backend to allow to deploy Capella instances.
* Fix log-on credentials for Azure AD (client/application id and secret)

Make sure `commands/install.sh` is referring to `options.local.yml`.

```
k3d cluster edit ertms --add-port "8000:80@loadbalancer"
```
