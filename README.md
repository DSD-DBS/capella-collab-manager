# Capella Collaboration Manager

A web platform for collaboration on [Capella](https://www.eclipse.org/capella/)
(MBSE) projects

**Copyright 2021, 2022 [DB Netz AG](https://fahrweg.dbnetze.com/),
licensed under Apache 2.0 License (see full text in [LICENSE](./LICENSE) file)**

Turn your local Capella experience into a browser-based collaboration platform for
model-based projects. Designed to enable co-working across multiple organizations.
Here are some of the key features:

* Run Capella in a browser
* Supports both git and [Team for Capella](https://www.obeosoft.com/en/team-for-capella)
  co-working models
* Single sign on (SSO) via [OAuth2](https://oauth.net/2/)
* No need to install or maintain local Capella clients - clients are made on demand in
  an underlaying [Kubernetes](https://kubernetes.io/) cluster
* Access to projects and models is self-managed by project leads, model owners or
  delegates
* Within a project a user could have read or read/ write access. Read-only users don't
  consume licenses in Team for Capella projects
* Integration with git repository management for backup and workflow automation around
  the models

We have more exciting features on our roadmap, for instance:

* an integration of templates
* a planning and release management for model-derived artifacts like documents,
  interface definitions, spreadsheets, etc.

## Getting started

### Running locally with k3d

#### Prerequisites

To deploy the application you need:

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/docs/intro/install/)

If you'd like to run it locally, these tools are additionally required:

* [k3d](https://k3d.io/) - a lightweight k8s cluster simulator
* `nss-myhostname` to access local container registry
  (on Ubuntu you can get it via `sudo apt install libnss-myhostname`)

When you have all that installed you can do the following:

```zsh
git clone --recurse-submodules https://github.com/DSD-DBS/capella-collab-manager.git
cd capella-collab-manager
```

Create a local k3d cluster and deploy the application

```zsh
make create-cluster
make deploy
```

It can take a long time to run, but shouldn't take more than 5 minutes. Meanwhile, the following message appears several times:
```
ready.go:277: [debug] Deployment is not ready: t4c-manager/dev-t4c-manager-backend. 0 out of 1 expected pods are ready
```
This is nothing to worry about - it just takes a while for all containers to start.

Verify your deployment - components should be in the "Running" state:

```zsh
kubectl get pods --namespace=t4c-manager
```

If something goes wrong, please open an issue on Github.

To clean up the environment run:

```zsh
make delete-cluster
```

#### Starting a session

Once the cluster is installed and all services are running (`kubectl get pods`), you can
get started. Follow our [Getting started guide](doc/getting_started.md) and be up and
running in a few minutes.

### Deployment

### Install on a cluster

1. Ensure your `kubectl` configuration points to the right cluster
2. Copy `helm/values.yaml` to `deployments/yourinstance.values.yaml`
3. Set all required values in the `deployments/yourinstance.values.yaml` configuration file
4. Create your sessions namespace in your kubernetes cluster: 
    ```
    kubectl create namespace <your-namespace>
    ```
5. Run the following command to deploy to your kubernetes cluster:
    ```
    helm install production -n <namespace> -f deployments/yourinstance.values.yaml helm
    ```
6. Set up the database for guacamole

### Upgrade an cluster instance

1. Ensure your `kubectl` configuration points to the right cluster
2. Compare `helm/values.yaml` with your `deployments/yourinstance.values.yaml` and update your configuration accordingly.
3. Run the following command to deploy to your kubernetes cluster:
    ```
    helm upgrade production -n <namespace> -f deployments/yourinstance.values.yaml helm
    ```

### Team for Capella integration

TODO

## How it works

Here comes a brief intro into architecture of this thing (TODO)

## Contributing

We'd love to see your bug reports and improvement suggestions! Please take a look at
[guidelines for contributors](CONTRIBUTING.md).
You'll also find instructions on how to set up a local development environment.
