<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## Authentication via Personal Access Token (Requires a Running Frontend)

Find more information about authentication with personal access tokens in the
user documentation: [Authentication](../../user/tokens.md)

As soon as you have a PAT (Personal Access Token) you can authenticate without
the application frontend.

## Authentication without Application Frontend

Request the `auth_url`

```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/authentication/' \
  -H 'accept: application/json'
```

Opening the `auth_url` in a browser leads you to a "Mock OAuth2 Server Sign-in"
page.

Login as user `admin` to be redirected to a page that is reachable when the
frontend runs. Anyway the redirect URL in the browser's address input field
contains two parameters `code` and `status`.

Example:

<pre>
    http://localhost:4200/oauth2/callback?...
    ...code=<span style="color:green">MREy4raZT9JqaYn_50yJraU4zkclGQbNcbudW404ekc</span>...
    ...&state=<span style="color:green">r7huaqqdDBWTb8x4gUDIpt36izM0Au</span>
</pre>

One must copy these parameters and post them via a second request returning an
access token:

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

To send a request using that token you may want to request the list of
projects:

```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/projects/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN>'
```

whereby `<TOKEN>` must be replaced by the token you received above.

Using the Swagger UI one can click on the lock symbols to enter the access
token.
