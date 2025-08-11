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
- If the tool is exposed via RDP, it must accept basic authentication. For
  HTTP-based tools, authentication is handled automatically via
  pre-authentication.
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
        <td>`CAPELLACOLLAB_SESSION_COOKIE`</td>
        <td>`eyJhbGciOiJSUzI1N[...]V1EFxboar4jmZBmFA94fQf9284;`</td>
        <td>
            `ccm_session_token` cookie, which external tools can use to authenticate the user.
            <hr style="margin-bottom:4px">
            :octicons-info-16: This is only available inside the redirect URL
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_SESSION_API_TOKEN`</td>
        <td>`collabmanager_0KCYg7Rt3AzurbZgvTO74GEQzIoOg1DK`</td>
        <td>
            Token which can be used against the Collaboration Manager API.
            More information [here](#internal-communication).
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
        <td>`CAPELLACOLLAB_SESSION_REQUESTER_USER_ID`</td>
        <td>`123`</td>
        <td>The ID of the user who has requested the session.</td>
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
        <td>`CAPELLACOLLAB_SESSION_PROVISIONING`</td>
        <td>
          <div style="width: 300px">
            ```json
            [
                {
                    "url": "https://github.com/DSD-DBS/coffee-machine",
                    "revision": "main",
                    "depth": 1,
                    "entrypoint": "coffee-machine-demo.aird",
                    "nature": "model",
                    "path": "/models/coffee-machine/coffee-machine"
                }
            ]
            ```
          </div>
        </td>
        <td>
            A list of dictionaries containing information about the models that were provisioned by the Collaboration Manager in the JSON format.

            Each list item contains the following attributes: <br>
            - `url`: The URL of the Git repository. <br>
            - `revision`: The revision of the Git repository. <br>
            - `depth`: The depth that was used while cloning the Git repository. <br>
            - `entrypoint`: The entrypoint of the Git repository. <br>
            - `nature`: The nature of the model in the Collaboration Manager. <br>
            - `path`: The path to the model in the session. <br>
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
    <tr>
        <td>`CAPELLACOLLAB_API_BASE_URL`</td>
        <td>`http://dev-backend.collab-manager.svc.cluster.local:/api`</td>
        <td>
            The API URL of the Collaboration Manager. The URL is only available from the session itself.
        </td>
    </tr>
    <tr>
        <td>`WORKSPACE_DIR`</td>
        <td>`/workspace`</td>
        <td>
            The directory of the (persistent) workspace the application should work with.
        </td>
    </tr>

</table>

##### TeamForCapella variables

In addition, the following variables are mounted if the TeamForCapella
integration is enabled for the tool and the session type is `persistent`.

For an explanation of those variables, refer to the
[Capella Docker images documentation](https://dbinfrago.github.io/capella-dockerimages/capella/t4c/base/#run-the-container).

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
You can use f-string formatting with all pre-defined environment variables, but
also define static variables.

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

Since version 3.1.0 of the Collaboration Manager, it is no longer necessary for
the tool itself to handle the authentication. Instead, the Collaboration
Manager automatically authenticates all users via pre-authentication with
session tokens.

### Internal communication

Sessions can communicate with the Collaboration Manager API. In addition,
sessions of the same user can communicate via inter-session communication.

Here is an example of how to use the API to identify another session and send a
request to it. You can run the code from a Jupyter session.

```py
import os
import requests

backend_url = os.getenv("CAPELLACOLLAB_API_BASE_URL")
user_id = os.getenv("CAPELLACOLLAB_SESSION_REQUESTER_USER_ID")
username = os.getenv("CAPELLACOLLAB_SESSION_REQUESTER_USERNAME")
pat = os.getenv("CAPELLACOLLAB_SESSION_API_TOKEN")

response = requests.get(f"{backend_url}/v1/users/{user_id}/sessions", auth=(username, pat))

internal_endpoint = response.json()[0]["internal_endpoint"]
requests.get(f"http://{internal_endpoint}").content
```

### Logging

The Capella Collaboration Manager collects logs of sessions automatically and
makes them available in Grafana for monitoring.

- The logs must be written to disk, stdout and stderr of the container are not
  persisted.
- The log collector scans all files with a file ending of `.log` below
  `/var/log/session` (Subdirectories are scanned too, but avoid large file
  structures).
- _Optional:_ For better filtering and searching, log the messages in the
  [logfmt](https://brandur.org/logfmt) format. Grafana Loki has an inbuilt
  parser for logfmt.

## Configuration examples

To help you configure your tools, we provide some examples as part of our
[Capella Docker images repository](https://github.com/dbinfrago/capella-dockerimages)

=== "Capella/Papyrus/Eclipse"

    ```yaml
    name: Eclipse # (1)
    integrations:
      t4c: true # (2)
      pure_variants: false # (3)
    config:
      resources:
        cpu:
          requests: 0.4
          limits: 2
        memory:
          requests: 1.6Gi
          limits: 6Gi
      environment:
        RMT_PASSWORD: "{CAPELLACOLLAB_SESSION_TOKEN}"
        ECLIPSE_PROJECTS_TO_LOAD: "{CAPELLACOLLAB_SESSION_PROVISIONING}"
      connection:
        methods:
          - id: guacamole
            type: guacamole
            name: Guacamole
            description: Guacamole doesn't support session sharing.
            ports:
              metrics: 9118
              rdp: 3389
            environment:
              CONNECTION_METHOD: xrdp
          - id: xpra
            type: http
            name: Xpra
            description: Xpra supports session sharing.
            ports:
              metrics: 9118
              http: 10000
            environment:
              XPRA_SUBPATH: "{CAPELLACOLLAB_SESSIONS_BASE_PATH}"
              CONNECTION_METHOD: xpra
              XPRA_CSP_ORIGIN_HOST: "{CAPELLACOLLAB_ORIGIN_BASE_URL}"
            redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/?floating_menu=0&sharing=1&path={CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
            cookies:
              token: "{CAPELLACOLLAB_SESSION_TOKEN}"
      monitoring:
        prometheus:
          path: /prometheus
      provisioning:
        directory: /models
        max_number_of_models: null
      persistent_workspaces:
        mounting_enabled: true
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
    config:
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
        JUPYTER_ADDITIONAL_DEPENDENCIES: ""
      connection:
        methods:
          - id: jupyter
            type: http
            name: Direct Jupyter connection (Browser)
            description: The only available connection method for
              Jupyter.
            ports:
              metrics: 9118
              http: 8888
            environment: {}
            redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/lab?token={CAPELLACOLLAB_SESSION_TOKEN}"
            cookies: {}
            sharing:
              enabled: True
      monitoring:
        prometheus:
          path: /prometheus
      provisioning:
        directory: /models
        max_number_of_models: null
      persistent_workspaces:
        mounting_enabled: true
    ```
