# Capella Collaboration Manager

A web platform for collaboration on Capella (MBSE) projects

**Copyright 2021, 2022 DB Netz AG, licensed under Apache 2.0 License (see full text in LICENSE file)**

Turn your local Capella experience into a browser-based collaboration platform for model-based projects. Designed to enable co-working across multiple organizations.
Here are some of the key features:

* Run Capella in a browser
* Supports both git and TeamForCapella co-working models
* SSO via OAuth2
* No need to install or maintain local Capella clients - clients are made on demand in a underlaying Kubernetes cluster
* Access to projects and models is self-managed by project leads, model owners or delegates
* Within a project a user could have read or read/write access. Read-only users don't consume licenses in TeamForCapella projects
* Integration with git repository management for backup and workflow automation around the models

We have more exciting features on our roadmap, like integration of templates, planning and release management for model-derived artifacts (documents, interface definitions, spreadsheets, etc.)

# Getting started

## Requirements

## Running locally with K3D

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
git clone --recurse-submodules https://github.com/DSD-DBS/capella-collab-manager.git
cd capella-collab-manager
make create-cluster  # this creates cluster and container registry
```

At this point, have a look at the [frondend README](frontend/README.md) in order to configure the frontend.
You'll need an `environment.prod.ts` file in the right location.

To build the Capella images you'll need to download Capella (binary!) and copy the archive to `capella-dockerimages/capella/archives`. For instructions, please refer to the [capella-dockerimages' README](capella-dockerimages/README.md).

Once you've configured the frontend and capella images, continue with your deployment:

```
MY_EMAIL=me@mydomain.com make deploy  # build and deploy the manager app
kubectl get pods --namespace=t4c-manager  # verify your deployment - components should be in "Running" state
```

Replace `me@domain.com` with your e-mail address. An administrator account will be made for this user.

Important! If you use Windows and the Git Bash to execute the commands, you have to set the environment variable: `MSYS_NO_PATHCONV=1`. 
Otherwise the commands will break with UNIX paths, because the Git Bash tries to add a Windows path prefix. 

If something goes wrong, please open an issue on Github.

If something goes wrong, please open an issue on Github.

To clean up the environment, simply run:

```
make delete-cluster
```

## Deployment

## Running on a cluster

* Ensure your `kubectl` configuration points to the right cluster
* Run `MY_EMAIL=me@mydomain.com make deploy` to deploy to your kubernetes cluster.

## TeamForCapella integration

TODO

# How it works

Here comes a brief intro into architecture of this thing (TODO)

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a look at [guidelines for contributors](CONTRIBUTING.md).
You'll also find instructions on how to set up a local development environment.
