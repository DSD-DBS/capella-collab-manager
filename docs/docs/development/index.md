<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Thanks for your interest in our project. Contributions are always welcome!

We are committed to fostering a welcoming, respectful, and harassment-free
environment. Be kind!

If you have questions, ideas or want to report a bug, feel free to
[open an issue](https://github.com/DSD-DBS/capella-collab-manager/issues). Or
go ahead and
[open a pull request](https://github.com/DSD-DBS/capella-collab-manager/pulls)
to contribute code. In order to reduce the burden on our maintainers, please
make sure that your code respects the
[acceptance criteria for pull requests](./pull_requests.md).

!!! info

    The "Developer Documentation" focuses on the development of the Collaboration Manager itself.
    If you want to use our API to automate tasks, refer to the [API documentation](../api/index.md) instead.

## Setup of a Local Development Environment

In addition to the
[local k3d deployment](https://github.com/DSD-DBS/capella-collab-manager#running-locally-with-k3d),
we have a local development environment. This environment includes automatic
reloading of the frontend and backend, providing direct feedback instead of
long build iterations.

In any case, start with the
[local k3d deployment](https://github.com/DSD-DBS/capella-collab-manager#running-locally-with-k3d).
The k3d cluster is required for the development environment.

### Requirements

- [`Python`](https://www.python.org/) >= 3.12
- [`Docker`](https://www.docker.com/)
- [`GNU Make`](https://www.gnu.org/software/make/)
- [`Node.js`](https://nodejs.org/en) >= v20.8.0
- [`npm`](https://www.npmjs.com/) package manager
- [`Angular CLI`](https://angular.dev/tools/cli/setup-local#install-the-angular-cli)

### Backend Configuration

The backend uses various configuration settings. You can find them in the
`backend/config` directory. A `config.yaml` with default values will be
generated the first time you run the application.

_Hint_: If you already have the
[local k3d deployment](https://github.com/DSD-DBS/capella-collab-manager#running-locally-with-k3d)
running, then no configuration values need to be adjusted.

### Getting Started

To get started, run the following command in the root of the repository for the
initial setup (only required once):

```zsh
(cd backend && make install)
(cd frontend && npm i)
(cd docs && make install)
```

Then, run the following command to start the dev environment:

```zsh
make dev
```

If everything went well, the frontend and backend should be running now:

- [Frontend](http://localhost:4200)
- [Backend healthcheck](http://localhost:8000/healthcheck)
- [Backend API documentation](http://localhost:8000/docs)
- [Documentation](http://localhost:8081)
- [Storybook](http://localhost:6006)

### Spawn and Access Sessions in the Cluster

You can also spawn sessions in the development environment, but it requires a
running
[local k3d deployment](https://github.com/DSD-DBS/capella-collab-manager#running-locally-with-k3d).

Sessions are secured with pre-authentication. If you use the same private key
in the cluster and locally, the token issued in the development environment
will also be accepted in the development k3d cluster. To synchronize the keys,
run the following command:

```zsh
make synchronize-rsa-keys
```

## General Notes

### REST APIs

We use REST APIs for the communication between frontend and backend. Please
follow the
[RESTful web API design best practises](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design).

### Git

The commit messages have to follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification)
specification.

In general, we use pre-commit hooks to enforce coding standards. To set up the
pre-commit hooks, please run the following commands:

```zsh
pip install -U pip pre-commit
pre-commit install
```
