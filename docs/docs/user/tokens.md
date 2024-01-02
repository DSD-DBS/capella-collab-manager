<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Authentication with Personal Access Tokens (PAT)

To authenticate against the API you can either use a Bearer token (which the
browser usually uses) or authenticate with a longer lived personal access token
(PAT) which can be used e.g. in scripts.

## PAT Creation

To create a personal access token (PAT) you can go to Profile > Token and
insert a short description and pick a date until when the token should be
valid.

<!-- prettier-ignore -->
!!! info
    The password which is generated can only be copied once. Make sure you save
    it - you won't be able to access it again

## PAT Scope

Personal access token have the same scope as the user who created it. It is
therefore important that you never pass on the token and treat it responsibly.
If you feel that the token has been lost, revoke it immediately and inform the
Systems Engineering Toolchain team.

## Revoke a PAT

In order to revoke a token go to Profile > Token. There you can see a list of
all tokens that belong to your user. By clicking on the trash symbol, you can
delete a token, which will no longer be valid for authentication.

## PAT Usage

The token created is a personal access token. There are different ways to
authenticate with that against the Collaboration Manager API. One example is:

```zsh
curl -u [username]:[token] https://[baseURL]/api/v1/projects
```

Another example is working with the diagram cache of py-capellambse. The
implementation of the capella modelling tool `capellambse` uses Python and lets
you read and write models. For more information have a look at the
[documentation](https://dsd-dbs.github.io/py-capellambse/) or the
[Github repository](https://github.com/DSD-DBS/py-capellambse).

```python
model = capellambse.model.MelodyModel(
  path="<path to the model on your machine>",
  diagram_cache={
    "path": "https://<your backend url>/api/v1/projects/<your project slug>/models/<your model slug>/diagrams/%s",
    "username": "<username>",
    "password": "<your PAT>",
  }
)
```

Having created a model like that you can e.g. with `model.diagrams[0]` get the
first diagram.
