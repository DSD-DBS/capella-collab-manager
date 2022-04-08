# A web platform for collaboration on Capella (MBSE) projects

**Copyright 2021 DB Netz AG, licensed under Apache 2.0 License (see full text in LICENSE file)**

Turns local Capella experience into a browser-based collaboration platform for model-based projects. Designed to enable co-working across multiple organizations.
Here are some of the key features:

* Supports both git and TeamForCapella co-working models
* SSO via OAuth2
* No need to install or maintain local Capella clients - clients are made on demand in a underlaying Kubernetes cluster
* Access to projects and models is self-managed by project leads, model owners or delegates
* Within a project a user could have read or read/write access. Read-only users don't consume licenses in TeamForCapella projects
* Integration with git repository management for backup and workflow automation around the models

We have more exciting features on our roadmap, like integration of templating, planning and release management for model-derived artifacts (documents, interface definitions, spreadsheets, etc.)

# Getting started

## Requirements

Here is a short summary of what you would need to run this environment: TODO

## Running locally with k3d

To run this thing locally you'll need:
* a Linux machine
* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/docs/intro/install/)
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

TODO: it fails at this point, need to find a way to fix it
TODO

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

TODO

## TeamForCapella integration

TODO

# How it works

Here comes a brief intro into architecture of this thing (TODO)

# Contributing

TODO
