<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Collaboration Manager

[![REUSE status](https://api.reuse.software/badge/github.com/DSD-DBS/capella-collab-manager)](https://api.reuse.software/info/github.com/DSD-DBS/capella-collab-manager)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![lint](https://github.com/DSD-DBS/capella-collab-manager/actions/workflows/lint.yml/badge.svg)
![tests](https://github.com/DSD-DBS/capella-collab-manager/actions/workflows/tests.yml/badge.svg)
![push](https://github.com/DSD-DBS/capella-collab-manager/actions/workflows/push.yml/badge.svg)
[![codecov](https://codecov.io/github/DSD-DBS/capella-collab-manager/branch/main/graph/badge.svg?token=1UZHL2H54F)](https://codecov.io/github/DSD-DBS/capella-collab-manager)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/capella-collab-manager)](https://artifacthub.io/packages/search?repo=capella-collab-manager)

A web platform for collaboration on MBSE and
[Capella](https://www.eclipse.org/capella/) projects.

**Copyright 2021 - 2025 [DB InfraGO AG](https://dbinfrago.com/), licensed under
Apache 2.0 License (see full text [here](./LICENSES/Apache-2.0.txt))**

Turn your local MBSE and Capella experience into a browser-based collaboration
platform for model-based projects. Designed to enable co-working across
multiple organizations. Here are some of the key features:

- Run MBSE related tools (Capella, Papyrus, Eclipse, pure::variants, Jupyter,
  etc.) in a browser
- Supports both Git and
  [Team for Capella](https://www.obeosoft.com/en/team-for-capella) co-working
  models
- Single sign-on (SSO) via [OAuth2](https://oauth.net/2/)
- No need to install or maintain local Capella clients - clients are made on
  demand in an underlying [Kubernetes](https://kubernetes.io/) cluster
- Access to projects and models is self-managed by project admins, model owners
  or delegates
- Within a project a user could have read or read & write access. Read-only
  users don't consume licenses in Team for Capella projects.
- Integration with Git repository management for backup and workflow automation
  around the models.
- Diagram cache integration: Display Capella diagrams in the browser within
  seconds.
- Model badge integration: Each model displays an automatically generated model
  complexity badge.
- Automatic "garbage collection": Unused sessions are terminated to free up
  resources and reduce cost.
- Jupyter integration to talk to Capella models from the workspace and to
  automate tasks.

In addition, we have integrated commercial products:

- [Team for Capella](https://www.obeosoft.com/en/team-for-capella):
  - Automatic repository monitoring
  - UI to create and delete models
  - Automatic license injection into sessions.
  - Synchronization from TeamForCapella repositories to Git repositories
  - Automatic access management via session tokens.

- [pure::variants](https://www.pure-systems.com/purevariants)
  - Automatic license injection
  - Access to licenses is self-managed by project admins

We've prepared a small video, where we showcase the diagram cache feature and
show how you can use Capella and Jupyter in split view in the browser:

https://github.com/DSD-DBS/capella-collab-manager/assets/23395732/01c5dc34-7792-4858-a87a-3205927b3d00

## Getting Started

### Running Locally with k3d

The following instructions are not suitable for a production deployment, but
can be used to try out the features of the Collaboration Manager locally. You
can find the installation guide for a production deployment in the
[general documentation](https://dsd-dbs.github.io/capella-collab-manager/admin/installation/).

#### Prerequisites

To deploy the application you need:

- [Docker](https://docs.docker.com/engine/install/ubuntu/) >= 20.10.X
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) >=
  1.24 (Stargazer)
- [helm](https://helm.sh/docs/intro/install/) >= 3.9.X
- [Make](https://www.gnu.org/software/make/manual/make.html) >= 3.82,
  recommended 4.X
- [Python](https://www.python.org/downloads/) >= 3.10

If you'd like to run it locally, these tools are additionally required:

- [k3d](https://k3d.io/) - a lightweight k8s cluster

When you have all that installed you can do the following:

```zsh
git clone --recurse-submodules https://github.com/DSD-DBS/capella-collab-manager.git
cd capella-collab-manager

# Create a local k3d cluster and test the registry reachability
make create-cluster reach-registry
```

Then, choose one of the four options and run the corresponding command. The
options can be changed at any time later:

<!-- prettier-ignore -->
> [!NOTE]
> Currently, we only provide amd64 images. If you want to run the
> application on arm64, you need to build the images yourself (option 3 or 4).

<!-- prettier-ignore -->
> [!NOTE]
> Since version v4.21.0, Guacamole is no longer deployed by default in local environments.
> If you want to use Guacamole, you need to set the environment variable `DEPLOY_GUACAMOLE=1`.

1. Fetch management portal and session images from GitHub (without
   TeamForCapella support). This option is recommended for the first
   deployment.

   ```zsh
   export DOCKER_REGISTRY=ghcr.io/dsd-dbs/capella-collab-manager
   export CAPELLACOLLAB_SESSIONS_REGISTRY=ghcr.io/dsd-dbs/capella-dockerimages
   DEVELOPMENT_MODE=1 make helm-deploy open
   ```

1. Build management portal images and fetch session images from GitHub (without
   initial TeamForCapella support)

   ```zsh
   export CAPELLACOLLAB_SESSIONS_REGISTRY=ghcr.io/dsd-dbs/capella-dockerimages
   DEVELOPMENT_MODE=1 make build helm-deploy open rollout
   ```

1. Build management portal and session images locally (without initial
   TeamForCapella support) \
   To reduce the build time, the default configuration only builds images for
   Capella 6.0.0. If you want to build more images for different versions, set
   the environment variable `CAPELLA_VERSIONS` with a space-separated list of
   semantic Capella versions.

   ```
   export CAPELLA_VERSIONS="6.0.0 6.1.0"
   export BUILD_ARCHITECTURE=amd64 # or arm64
   ```

   Then, run the following command:

   ```
   DEVELOPMENT_MODE=1 make deploy
   ```

1. Build Capella and TeamForCapella images locally (with initial TeamForCapella
   support)

   Read and execute the preparation in the Capella Docker images documentation:
   [TeamForCapella client base](https://dsd-dbs.github.io/capella-dockerimages/capella/t4c/base/#preparation).

   Then, run the following command:

   ```
   DEVELOPMENT_MODE=1 make deploy-t4c
   ```

It can take a long time to run, but shouldn't take more than 5 minutes. Please
wait until all services are in the "Running" state.

If all goes well, you should find Capella Collaboration Manager running on
<https://localhost:443/>.

If you want to see the individual services in the web-based Kubernetes
dashboard, you can run the following command:

```zsh
make dashboard
```

If something goes wrong, please open an issue on GitHub.

To clean up the environment, run:

```zsh
make delete-cluster
k3d registry delete k3d-myregistry.localhost
```

#### Starting a Session

Once the cluster is installed and all services are running
(`kubectl get pods`), you can get started. Follow our
[Getting started guide](https://dsd-dbs.github.io/capella-collab-manager/admin/getting_started/getting_started/)
and be up and running in a few minutes.

## How it Works

The Capella Collaboration Manager consists of a couple of components:

- A frontend - what you see in the browser
- A backend service - for managing projects, users and sessions
- [Guacamole](https://guacamole.apache.org/), to expose the sessions via the
  browser
- Databases, for state persistence
- Prometheus for session monitoring
- Grafana Loki for logs management

External software can also be linked. These parts can be installed separately:

- Optional: A Git server (used for read-only sessions and Git backups)
- Optional: A Team for Capella server
- Optional: A pure::variants server

## Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our
[developer documentation](https://dsd-dbs.github.io/capella-collab-manager/development/).
You'll also find instructions on how to set up a local development environment.
