<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Contributing

Thanks for your interest in our project. Contributions are always welcome!

We are committed to fostering a welcoming, respectful, and harassment-free
environment. Be kind!

If you have questions, ideas or want to report a bug, feel free to [open an
issue](/../../issues). Or go ahead and [open a pull request](/../../pulls) to contribute
code. In order to reduce the burden on our maintainers, please make sure that
your code follows our style guidelines outlined below.

## General

This project consists of several services. Here is the architecture of the services:
![Capella Collab Manager architecture](docs/architecture.png)

To get an overview of the services, it is also worth taking a look at the Helm Chart,
which can be found in the `helm` folder.

We use REST APIs for the communication between frontend and backend.
Please follow the [RESTful web API design best practises](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design).

We recommend to get started with the [local k8d deployment](README.md).

<!-- prettier-ignore -->
By default, the services run on the following ports when using the instructions below:
| Port  | Service             |
|-------|---------------------|
| 8080  | k3d deployment      |
| 12345 | k3d registry        |
| 4200  | frontend            |
| 8000  | backend             |
| 8081  | t4c-server mock     |
| 8082  | license-server mock |
| 8083  | oauth-mock          |

## Git

The commit messages have to follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification) specification.

In general, we use pre-commit hooks to enforce coding standards.
To setup the pre-commit hooks, please run the following commands:

```zsh
pip install -U pip pre-commit
pre-commit install -t pre-commit -t commit-msg
```

## Capella Docker images

Please follow the [README of the Capella Docker images repository](/../../../capella-dockerimages/blob/main/README.md).
When all files are in the right place, you can execute the following command to build
and push the Docker images.

```sh
make capella-dockerimages
```

## OAuth Server

We use OAuth2 as authentication protocol for our application. Therefore we need an
OAuth2 server. For local development, we have an OAuth mock that needs to be started
first.

Do not use the OAuth mock in production!

First of all, navigate to the `mocks/oauth` directory.

1. Run the OAuth2-Mock-Server with:

   ```sh
   make start
   ```

2. Verify that the server runs, e.g., by navigating to
   [Well Known](http://localhost:8083/default/.well-known/openid-configuration)

## Backend

Requirements:

- `python` and `pip`
- `docker`
- `make`

Run the following steps:

1. In the project's root directory you must create a local k3d cluster by running

   ```sh
   make create-cluster
   ```

1. In order to use Guacamole, the cluster must be deployed:

   ```sh
   make deploy
   ```

1. Navigate to the `backend` directory of your cloned repository.
1. We recommend that you develop inside of a virtual environment. To set it up,
   run the following commands:

   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -U pip setuptools
   pip install -e '.[dev]'
   ```

1. The backend uses various configuration settings. You can find them in the `config`
   directory.
   Please copy the file `config_template.yaml` to `config.yaml` and adjust the values.

   _Hint_: If you already have the k8d cluster running and if you have the
   application deployed, then no configuration values need to be adjusted.

   _Hint_: You can run `python -m capellacollab.config.diff` after each update to check if your config is up to date.

1. This step is only **necessary, if you use the self signed certificate** option for the oauth mock.

   If you don't have the certificate in your local certificate store, please execute the following command:

   ```sh
   export REQUESTS_CA_BUNDLE=$(pwd)/../certs/localhost.crt
   ```

   You need to adjust the option `authentication.oauth.endpoints.wellKnown` in the `config.yaml` to the following value:

   ```text
   https://localhost:8083/default/.well-known/openid-configuration
   ```

1. To begin the development a PostgreSQL database is required. To run the database and
   start the backend run:

   ```sh
   make dev
   ```

1. You should see it running on port 8000.

   - [Healthcheck](http://localhost:8000/healthcheck)
   - [Documentation](http://localhost:8000/docs)

We additionally recommend that you set up your editor / IDE as follows.

- Indent with 4 spaces per level of indentation
- Maximum line length of 79 (add a ruler / thin line / highlighting / ...)
- Set up the editor to run `black`, `pylint`, `mypy` and `isort` when saving.

### Create database migrations scripts

To create an upgrade script automatically (this will compare the current database state
with the models):

```sh
alembic revision --autogenerate -m "Commit message"
```

## Authentication without application frontend

Request the `auth_url`

```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/authentication/' \
  -H 'accept: application/json'
```

Opening the `auth_url` in a browser leads you to a "Mock OAuth2 Server Sign-in" page.

Login as user `admin` to be redirected to a page that is reachable when the frontend
runs. Anyway the redirect URL in the browser's address input field contains two
parameters `code` and `status`.

Example:

<pre>
    http://localhost:4200/oauth2/callback?...
    ...code=<span style="color:green">MREy4raZT9JqaYn_50yJraU4zkclGQbNcbudW404ekc</span>...
    ...&state=<span style="color:green">r7huaqqdDBWTb8x4gUDIpt36izM0Au</span>
</pre>

One must copy these parameters and post them via a second request returning an access
token:

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/authentication/tokens' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "code": "MREy4raZT9JqaYn_50yJraU4zkclGQbNcbudW404ekc",
  "state": "r7huaqqdDBWTb8x4gUDIpt36izM0Au"
}'
```

To send a request using that token you may want to request the list of projects:

```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/projects/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN>'
```

whereby `<TOKEN>` must be replaced by the token you received above.

Using the Swagger UI one can click on the lock symbols to enter the access token.

## Frontend

Requirements:

- Node.js 18
- `npm` package manager
- [Angular CLI](https://angular.io/cli#installing-angular-cli)
- `make`

Run the following steps:

1. Navigate to the `frontend` folder
1. Install dependencies via `npm install`
1. Optional: If you like to use your custom favicon, please copy it to `src/favicon.ico`
1. Optional: If you like to use your custom theme, replace the file `src/custom-theme.scss`.
   You can generate custom themes [here](http://mcg.mbitson.com/)
1. Run the frontend with:

   ```sh
   make dev
   ```

1. You should see the frontend running on port 4200.

We additionally recommend that you set up your editor / IDE as follows.

- Set up the editor to run [prettier](https://prettier.io/) when saving.

## User documentation

Requirements:

- `python` + `pip`

Run the following steps:

1. Navigate to the `docs/user` directory of your cloned repository.
2. We recommend that you develop inside of a virtual environment. To set it up,
   run the following commands:

   ```zsh
   python -m venv .venv
   source .venv/bin/activate
   pip install -U pip setuptools
   ```

3. Install MkDocs Material:

   ```zsh
   pip install mkdocs-material
   ```

4. Serve the docs:

   ```zsh
   mkdocs serve
   ```

## Code style

You can find our code style rules [here](https://dsd-dbs.github.io/capella-collab-manager/code-style/)
