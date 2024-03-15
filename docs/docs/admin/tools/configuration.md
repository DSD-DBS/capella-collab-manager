<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Configuration of tools

## Getting started

To add a tool to the Collaboration Manager, it must fulfill the following
requirements:

- The tool must run in a single Docker container (no sidecar containers).
- The Docker container has to run with a non-root user.
- The Docker image has to be deployed to a Docker registry, which is accessible
  from the Collaboration Manager server environment.
- The tool must be exposed via RDP or HTTP/HTTPS.
- The tool must implement simple means of authentication. The accepted methods
  depend on the used connection method: <br /> **RPD**: Username/Password
  authentication via the RDP protocol. <br /> **HTTP**: Token via query
  parameter, local storage, basic authentication or cookies, more information
  [here](#authentication).
- The container must expose a `/metrics` endpoint with an `idletime_minutes`
  gauge metric in the OpenMetrics format, which returns the time in minutes
  since the last user interaction. The metric is used to determine if the
  session is idle and can be terminated.
- If you want to capture session logs and make them accessible via Grafana
  Loki, they have to be written to disk (stdout/stderr are not persisted).

## YAML Configuration

For a full documentation of all available options, refer to the
[API documentation](../../api/index.md).

### Resources

For each tool, you can define the resources which sessions of the tool can use.
This is a significant option because it impacts cost and performance.

An example configuration looks like this:

```yaml
resources:
  cpu:
    requests: 0.4
    limits: 2
  memory:
    requests: 1.6Gi
    limits: 6Gi
```

The values are Kubernetes resource requests and limits. More information is
available in the API documentation and the
[Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits).

### Environment variables

#### Predefined environment variables

##### General variables

We set the following environment variables for each session container. The
variables can be used by the tool:

<table markdown="span">
    <tr>
        <th style="width:40%">Environment Variable</th>
        <th style="width:20%">Example value</th>
        <th style="width:40%">Description</th>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSION_TOKEN`</td>
        <td>`KYYfLPiRVFijT7ZPhVx6DO0oPQcrfEInDetonD0nIKGnQmC9pWAfHq9xxKiYqUdj`</td>
        <td>
            Token, which the tool has to use to authenticate the user.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSION_ID`</td>
        <td>`tctszsirxuoohabwnhyhmzjdh`</td>
        <td>
            Unique Session ID of the session, can be used for API request to the Collaboration Manager API.
        </td>
    </tr>
        <tr>
        <td>`CAPELLACOLLAB_SESSION_CONNECTION_METHOD_TYPE`</td>
        <td>`guacamole`</td>
        <td>`http` or `guacamole`, depending on the requested connection method.</td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSION_REQUESTER_USERNAME`</td>
        <td>`janedoe`</td>
        <td>The username of the user who has requested the session.</td>
    </tr>
        <tr>
        <td>`CAPELLACOLLAB_SESSION_CONTAINER_PORT`</td>
        <td>`8080`</td>
        <td>
            The port that the application has to serve on.
            <hr style="margin-bottom:4px">
            :octicons-info-16: HTTP port if connection method is `http` and RDP port if the connection method is `guacamole`.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSIONS_SCHEME`</td>
        <td>`https`</td>
        <td>
            HTTP scheme, can be `http` or `https`
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSIONS_HOST`</td>
        <td>`sessions.example.com`</td>
        <td>
            The hostname of the sessions environment.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSIONS_PORT`</td>
        <td>`443`</td>
        <td>
            The port of the sessions environment. Can be different to the port in `CAPELLACOLLAB_ORIGIN_HOST` if the sessions run on a different port (e.g. in our local non-cluster development environment).
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSIONS_BASE_PATH`</td>
        <td>`/session/2037430`</td>
        <td>
            The base path that the session application has to serve requests on.
            <hr style="margin-bottom:4px">
            :warning: Only available if `CAPELLACOLLAB_SESSION_CONNECTION_METHOD_TYPE` is `http`.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_ORIGIN_BASE_URL`</td>
        <td>`https://frontend.example.com:443`</td>
        <td>
            The origin host of the Collaboration Manager.
            The tool has to set the `Content-Security-Policy` header to `frame-ancestors self {CAPELLACOLLAB_ORIGIN_HOST}`. Otherwise, the session viewer can't be used with the tool!
        </td>
    </tr>

</table>

##### TeamForCapella variables

In addition, the following variables are mounted if the TeamForCapella
integration is enabled for the tool and the session type is `persistent`.

For a explanation of those variables, refer to the
[Capella Docker images documentation](https://dsd-dbs.github.io/capella-dockerimages/capella/t4c/base/#run-the-container).

<table markdown="span" style=width:100%>
    <tr>
        <th style="width: 25%">Environment Variable</th>
        <th>Example value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>`T4C_LICENCE_SECRET`</td>
        <td>`1234123412341252435234523452345123423`</td>
        <td>License configuration for the TeamForCapella server.</td>
    </tr>
    <tr>
        <td>`T4C_JSON`</td>
        <td>
            ```json
            [
                {
                    "repository": "repoCapella",
                    "host": "localhost",
                    "port": 2036,
                    "instance": "default",
                    "protocol": "ssl"
                }
            ]
            ```
        </td>
        <td>JSON containing all repositories the user has access to. The format is described in the Capella Docker images documentation.</td>
    </tr>
    <tr>
        <td>`T4C_USERNAME`</td>
        <td>
            `admin`
        </td>
        <td>
            Username of the session requester on the TeamForCapella server.
            Can be used to authenticate against the repositories the user has access to.
        </td>
    </tr>
    <tr>
        <td>`T4C_PASSWORD`</td>
        <td>
            `adfaw34rfqadsc`
        </td>
        <td>
            Session token to authenticate against the TeamForCapella server.
            The token is auto-created and valid for all TeamForCapella repositories the user has access to.
        </td>
    </tr>
</table>

#### Definition of custom environment variables

If you don't have the possibility to set environment variables in your tool,
you can also define custom variables. You can also derive variables from
pre-defined values.

A variable is defined in the tool configuration:

```yaml
environment:
  MY_TOOL_USERNAME_WITH_PREFIX: 'test_{CAPELLACOLLAB_SESSION_REQUESTER_USERNAME}'
```

In this example, we map the `MY_TOOL_USERNAME` variable to the
`MY_TOOL_USERNAME_WITH_PREFIX` environment variable and add the `test_` prefix.
This is a powerful feature because you can use f-string formatting with all
pre-defined environment variables, but also define static variables.

### Connection methods

Each tool can support different connection methods. A connection methods
defines how the user connects to a session of the tool. You can define up to 10
connections methods for each tool. The user can select the preferred connection
method in the session request form.

#### Guacamole

To connect to RDP based tools, you can use our integration of
[Apache Guacamole](https://guacamole.apache.org/). The Collaboration Manager
will interact with the Guacamole API to create users and connections.

Guacamole will try to authenticate with the following credentials against the
RDP server. The RDP server has to run in the container and has to accept those
credentials:

```py
username="techuser"
password=CAPELLACOLLAB_SESSION_TOKEN
```

The configuration looks like:

```yaml
connection:
  methods:
    - identifier: <unique-identifier>
      type: guacamole
      name: Classic
      description: ''
      ports:
        metrics: 9118
        rdp: 3389
      environment:
        ENVIRONMENT_VARIABLE: test
```

#### HTTP(S)

You can use any web-based tool with the HTTP(S) connection method. The
configuration looks like:

```yaml
connection:
  methods:
    - identifier: <unique-identifier>
      type: http
      name: HTTP
      description: ''
      ports:
        metrics: 9118
        http: 10000
      environment:
        ENVIRONMENT_VARIABLE: test
      redirect_url: '{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}'
      cookies:
        token: '{CAPELLACOLLAB_SESSION_TOKEN}'
```

##### Authentication

We support different authentication methods for web-based tools. It's important
that the tool implements an authentication layer, otherwise users will be able
to connect to other sessions.

In general, we recommend to use a token based authentication approach. We
already generate a token for each session, which is available in the container
as `CAPELLACOLLAB_SESSION_TOKEN` environment variable.

To pass the token to the tool, you can use the following methods:

- **Cookies**: This is the recommended option. To use cookies for
  authentication, add a key/value pair to the `cookies` dictionary. The tool
  has to verify that the cookie value matches the token.
- **Token in the URL**: To pass the token as query parameter, edit the
  `redirect_url` and append `?token={CAPELLACOLLAB_SESSION_TOKEN}`. The tool is
  responsible to remove the token from the URL to prevent session hijacking
  attacks.
- **HTTP Basic Authentication**: If the tool only supports basic
  authentication, you can pass the token in the URL. Change the `redirect_url`
  to the format `https://username:{CAPELLACOLLAB_SESSION_TOKEN}@host.tld`. This
  option is hightly discouraged since some browsers have dropped support for it
  and other browsers will follow. Chrome has already removed support for basic
  authentication in subresources[^1], which means that the session viewer will
  not work. Also, it's vulnarable to session hijacking attacks when the user
  shares the URL.
- **Local storage**: To use cookies for authentication, add a key/value pair to
  the `local_storage` dictionary. Since the local storage is not shared between
  different ports on the same domain, sessions with the local storage method
  can't be used in the local non-cluster development environment.

[^1]: <https://chromestatus.com/feature/5669008342777856>

## Configuration examples

To help you configuring your tools, we provide some examples for the tools,
which we provide as part of our
[Capella Docker images repository](https://github.com/DSD-DBS/capella-dockerimages)

=== "Capella/Papyrus/Eclipse"

    ```yaml
    name: Eclipse # (1)
    integrations:
      t4c: true # (2)
      pure_variants: false # (3)
      jupyter: false
    sessions:
      resources:
        cpu:
          requests: 0.4
          limits: 2
        memory:
          requests: 1.6Gi
          limits: 6Gi
      environment:
        RMT_PASSWORD: "{CAPELLACOLLAB_SESSION_TOKEN}"
      connection:
        methods:
          - identifier: guacamole
            type: guacamole
            name: Classic
            description: "Old connection method using Guacamole. If
              it has worked fine previously, keep using it.
              In case of issues, try the Xpra connection
              method."
            ports:
              metrics: 9118
              rdp: 3389
            environment:
              CONNECTION_METHOD: xrdp
          - identifier: xpra
            type: http
            name: Xpra (experimental)
            description: "Experimental connection method using
              Xpra. It's intended for those users who have
              issues with the Guacamole connection method."
            ports:
              metrics: 9118
              http: 10000
            environment:
              XPRA_SUBPATH: "{CAPELLACOLLAB_SESSIONS_BASE_PATH}"
              CONNECTION_METHOD: xpra
              XPRA_CSP_ORIGIN_HOST: "{CAPELLACOLLAB_ORIGIN_BASE_URL}"
            redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/?floating_menu=0&path={CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
            cookies:
              token: "{CAPELLACOLLAB_SESSION_TOKEN}"
      monitoring:
        prometheus:
          path: /prometheus
    ```

    1. Use a clear and short name for the tool, e.g. `Capella`, `Papyrus` or `Eclipse`.

    2. Activate if `TeamForCapella` support is needed. Set it to `false` for `Papyrus` and `Eclipse`.

    3. For `pure::variants` support, set the value to `true`.

=== "Jupyter"

    ```yaml
    name: Jupyter
    integrations:
      t4c: false
      pure_variants: false
      jupyter: true
    sessions:
      resources:
        cpu:
          requests: 1
          limits: 2
        memory:
          requests: 500Mi
          limits: 3Gi
      environment:
        JUPYTER_PORT: "8888"
        JUPYTER_TOKEN: "{CAPELLACOLLAB_SESSION_TOKEN}"
        CSP_ORIGIN_HOST: "{CAPELLACOLLAB_ORIGIN_BASE_URL}"
        JUPYTER_BASE_URL: "{CAPELLACOLLAB_SESSIONS_BASE_PATH}"
      connection:
        methods:
          - identifier: jupyter
            type: http
            name: Direct Jupyter connection (Browser)
            description: "The only available connection method for Jupyter."
            ports:
              metrics: 9118
              http: 8888
            environment: {}
            redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/lab?token={CAPELLACOLLAB_SESSION_TOKEN}"
            cookies: {}
      monitoring:
        prometheus:
          path: /prometheus
    ```