# A web platform for collaboration on Capella (MBSE) projects

**Copyright 2021 DB Netz AG, licensed under Apache 2.0 License (see full text in LICENSE file)**

Turns local Capella experience into a browser-based collaboration platform for model-based projects. Designed to enable co-working across multiple organizations.
Here are some of the key features:

* Run Capella in a browser (spaw) - without installation of any software
* 
* Supports both git and TeamForCapella co-working models
* SSO via OAuth2
* No need to install or maintain local Capella clients - clients are made on demand in a underlaying Kubernetes cluster
* Access to projects and models is self-managed by project leads, model owners or delegates
* Within a project a user could have read or read/write access. Read-only users don't consume licenses in TeamForCapella projects
* Integration with git repository management for backup and workflow automation around the models

We have more exciting features on our roadmap, like integration of templating, planning and release management for model-derived artifacts (documents, interface definitions, spreadsheets, etc.)

# Getting started

## Requirements

## Running locally with k3d

### Prerequisites
To deploy the application you'll need:
* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/docs/intro/install/)

If you'd like to run it locally, these tools are additionally required:
* [K3D](https://k3d.io/) - a lightweight k8s cluster simulator
* `nss-myhostname` to access local container registry - you can get in on Ubuntu via `sudo apt install libnss-myhostname`

When you have all that installed you can simply do the following:

```
git clone --recurse-submodules ...; cd capella-collab-manager
make create-cluster  # this creates cluster and container registry
MY_EMAIL=me@mydomain.com make deploy  # build and deploy the manager app
kubectl get pods --namespace=t4c-manager  # verify your deployment - components should be in "Running" state
```

Important! If you use Windows and the Git Bash to execute the commands, you have to set the environment variable: `MSYS_NO_PATHCONV=1`. 
Otherwise the commands will break with UNIX paths, because the Git Bash tries to add a Windows path prefix. 

If something goes wrong, please open an issue on Github.

To clean up the environment, simply run:

```
make delete-cluster
```

## Deployment

## Running on a cluster

TODO

## TeamForCapella integration

TODO

# How it works

Here comes a brief intro into architecture of this thing (TODO)

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a look at [guidelines for contributors](CONTRIBUTING.md).
You'll also find instructions on how to set up a local development environment.