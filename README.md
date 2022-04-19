# Capella Collaboration Manager

A web platform for collaboration on Capella (MBSE) projects

**Copyright 2021 DB Netz AG, licensed under Apache 2.0 License (see full text in LICENSE file)**

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

To run this thing locally you'll need:
* a Linux machine
* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/docs/intro/install/)
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

If all goes well, you should find Capella-collab-manager running on http://localhost:8081/.

If something goes wrong, please open an issue on Github.

### Limitations

* Only works with Azure AD as authentication backend, create a small file `secrets.yaml` in this folder:

  ```yaml
  backend:
  oauth:
    authorizationEndpoint: https://login.microsoftonline.com/<tenant-id>
    usernameClaim: preferred_username
    
    client: 
      # OAUTH2 Client ID
      id: <client id, a.k.a. application id>
      # OAUTH2 Client Secret
      secret: <secret>
  ```

* When launching a Guacamole container, the local address (when testing on K3D) is wrong.
  Change the URL to point to port 8081.

## Running on a cluster

* Ensure your `kubectl` configuration points to the right cluster
* Run `MY_EMAIL=me@mydomain.com make deploy` to deploy to your kubernetes cluster.

## TeamForCapella integration

TODO

# How it works

![Capella Collab Manager architecture](doc/architecture.png)

The Capella Collaboration Manager consists of a couple of components:

* A frontend - what you see in the browser
* A backend web service - for managing users and sessions
* [Guacamole](https://guacamole.apache.org/), to expose the sessions via the browser
* Databases, for state persistence.
* Optional: A Teams4Capella server

Sessions are created in a separate namespace.

# Contributing

We'd love to see your bug reports and improvement suggestions! Please give us your feedback.