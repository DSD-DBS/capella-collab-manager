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
make sure that your code follows our style guidelines.

## Setup of a Local Development Environment

In addition to the
[local k8s deployment](https://github.com/DSD-DBS/capella-collab-manager#running-locally-with-k3d),
we have local development environment. This environment includes automatic
reloading of the frontend and backend.

### Requirements

- `Python` >= 3.11
- `Docker`
- `GNU Make`
- `Node.js 18` >= v20.8.0
- `npm` package manager
- [`Angular CLI`](https://angular.io/cli#installing-angular-cli)

### Backend Configuration

The backend uses various configuration settings. You can find them in the
`config` directory. Please copy the file `config_template.yaml` to
`config.yaml` and adjust the values.

_Hint_: If you already have the k8d cluster running and if you have the
application deployed, then no configuration values need to be adjusted.

_Hint_: You can run `python -m capellacollab.config.diff` after each update to
check if your config is up to date.

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
- [Capella Collaboration Manager Documentation](http://localhost:8081)

## General Notes

### REST APIs

We use REST APIs for the communication between frontend and backend. Please
follow the
[RESTful web API design best practises](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design).

### Git

The commit messages have to follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification)
specification.

In general, we use pre-commit hooks to enforce coding standards. To setup the
pre-commit hooks, please run the following commands:

```zsh
pip install -U pip pre-commit
pre-commit install
```
