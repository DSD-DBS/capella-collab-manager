<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Automate tasks with our API

Our API is designed to be simple and easy to use. It is based on RESTful
principles and uses standard HTTP methods. This means that you can use the API
to automate tasks such as creating and managing projects, sessions, and users.

!!! warning

    We try to keep the API as stable as possible, but we cannot guarantee that
    it will not change in the future. If you are using the API, make sure to
    check our [release notes](https://github.com/DSD-DBS/capella-collab-manager/releases)
    for any breaking changes.

## API Documentation

!!! note

    **The API documentation is only available via the documentation of Collaboration
    Manager instances** and GitHub Pages. Only in this case you'll be able to open the links below.
    You'll see the API documentation matching the version of the Collaboration Manager
    instance you are using.

    It is not available on:

    - Local non-cluster development environments
    - ReadTheDocs

Please use these links to access the API documentation:

- [:octicons-link-external-16: SwaggerUI](redirect/swagger.md) (Interactive
  SwaggerUI documentation)
- [:octicons-link-external-16: ReDoc](redirect/swagger.md) (Interactive ReDoc
  documentation)
- [:octicons-link-external-16: OpenAPI Specification, formerly Swagger Specification](redirect/swagger.md)
  (JSON)

## Authentication

To authenticate against the API you can use Personal Access Tokens (PAT).

### PAT Creation

To create a personal access token (PAT) you can go to `Menu` > `Tokens`. Every
token requires a title, description, and expiration date. In addition, the
token only has access to the provided scope. In the API documentation you'll
find the required permissions for each route.

!!! info

    The token which is generated will disappear after leaving the page.
    Make sure you save it - you won't be able to access it again.

!!! important

    All requests are made in the name of the user who issued the token
    and are logged accordingly. If you lose, share, or publish a token
    you must revoke it immediately and inform your system administrator team.

### Revoke a PAT

In order to revoke a token go to `Menu` > `Token`. There you can see a list of
all tokens that are associated with your account. By clicking on the delete
button, you can delete a token, which will no longer be valid for
authentication.

### PAT Usage

You can use the token in place of a password for basic authentication against
the API as in the following examples.

#### Example with Python

```py
import requests

base_url = "example.com" # Replace with the base URL of your Collaboration Manager instance
username = "..."
token = "..."

requests.get(
    f"https://{base_url}/api/v1/projects",
    auth=(username, token)
)
```

#### Example with cURL

With `cURL` you can use the following command to fetch the list of projects:

```zsh
curl -u ${USERNAME}:${TOKEN} https://${BASE_URL}/api/v1/projects
```

#### Example with `capellambse`

Another example is working with the diagram cache of py-capellambse. The
implementation of the Capella modelling tool `capellambse` uses Python and lets
you read and write models. For more information have a look at the
[documentation](https://dsd-dbs.github.io/py-capellambse/) or the
[GitHub repository](https://github.com/DSD-DBS/py-capellambse).

```python
import capellambse

base_url = "example.com" # Replace with the base URL of your Collaboration Manager instance
username = "..."
token = "..."
path_to_aird = "..."

model = capellambse.model.MelodyModel(
  path=path_to_aird,
  diagram_cache={
    "path": f"https://{base_url}/api/v1/projects/{project_slug}/models/{model_slug}/diagrams/%s",
    "username": username,
    "password": token,
  }
)
```
