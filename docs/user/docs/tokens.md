<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Token Authentication

To authenticate against the API you can either use a Bearer token (which the
browser usually uses) or authenticate with a longer lived basic authentication
token which can be used e.g. in scripts.

## Token Creation

To create a Token you can go to Profile > Token and insert a short description
to create a token.

 <!-- prettier-ignore -->

!!! info The password which is generated can only be copied. Make sure you save
it - you won't be able to access it again

## Token Scope

Basic authentication token have the same scope as the bearer token.

<!-- prettier-ignore -->
!!! warning
    As currently Basic Authentication token have the same scope as you logged in your browser they can act as your user. Please do not share the password and if the information gets lost please revoke the token as soon as possible.

## Revoke a Token

In order to revoke a token go to Profile > Token. There you can see a list of
all tokens that belong to your user. Clicking on the trash symbol you can
delete a token which will no longer be valid to authenticate.

## Token Usage

The token created is a basic authentication token. There are different ways to
authenticate with that against the Collaboration Manager API. One example is:

```zsh
curl --basic -u yourUsername:yourPassword https://baseurl/api/v1/users/current/tokens
```

or to work with the diagram cache

```python
capellambse.model.MelodyModel(
          path="path to the model on your machine",
          diagram_cache={
            "path": "https://baseurl/api/projects/[yourProjectSlug]/[yourModelName]/diagrams/%s",
            "username": "yourUsername",
            "password": "yourPassword",
          })
```
