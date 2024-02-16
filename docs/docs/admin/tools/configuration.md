<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Configuration of tools

## Getting started

To add a tool to the Collaboration Manager, it must fullfill the following
requirements:

- The tool must run in a single Docker container (no side-car containers).
- The Docker image is deployed to a Docker registry, which is accessible from
  the Collaboration Manager server environment.
- The tool must be exposed via RDP or HTTP/HTTPS.
- If you want to capture logs, they have to be written to disk (stdout/stderr
  are not persisted).

## YAML Configuration

For a full documentation of all available options, refer to the
[API documentation](../../api/index.md).

### Predefined environment variables

#### General variables

We set the following environment variables for each session container. The
variables can be used by the tool:

<table markdown="span">
    <tr>
        <th style="width:40%">Environment Variable</th>
        <th style="width:20%">Example value</th>
        <th style="width:40%">Description</th>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_TOKEN`</td>
        <td>`KYYfLPiRVFijT7ZPhVx6DO0oPQcrfEInDetonD0nIKGnQmC9pWAfHq9xxKiYqUdj`</td>
        <td>
            Token, which the tool has to use for basic authentication.
            <hr style="margin-bottom:4px">
            :warning: Only available if authentication type is basic authentication.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_REQUESTER_USERNAME`</td>
        <td>`maxmustermann`</td>
        <td>The username of the user who has requested the session.</td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_BASE_PATH`</td>
        <td>`/session/2037430`</td>
        <td>
            The base path that the application has to serve requests on.
            <hr style="margin-bottom:4px">
            :warning: Only available if `CAPELLACOLLAB_CONNECTION_METHOD` is `http`.
        </td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_CONNECTION_METHOD`</td>
        <td>`rdp`</td>
        <td>`http` or `rdp`, depending on the requested connection method.</td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_PORT`</td>
        <td>`8080`</td>
        <td>The port that the application should serve on.</td>
    </tr>
    <tr>
        <td>`CAPELLACOLLAB_CSP_ORIGIN_HOST`</td>
        <td>`http://localhost:8000`</td>
        <td>
            The origin host of the Collaboration Manager.
            The tool has to set the `Content-Security-Policy` header to `frame-ancestors self $CAPELLACOLLAB_CSP_ORIGIN_HOST`.
            Otherwise, the session viewer can't be used with the tool!
        </td>
    </tr>
</table>

#### TeamForCapella variables

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

#### Mapping of environment variables

If you don't have the possibility to set environment variables in your tool,
you can also map the predefined environment variables to custom names.

A mapping is defined in the tool configuration:

```yaml
mapping:
  - from: CAPELLACOLLAB_REQUESTER_USERNAME
    to: MY_TOOL_USERNAME
```

In this example, we map the `CAPELLACOLLAB_REQUESTER_USERNAME` variable to the
`MY_TOOL_USERNAME` environment variable. `CAPELLACOLLAB_REQUESTER_USERNAME` and
`MY_TOOL_USERNAME` are available as variables in the container and contain the
username of the Collaboration Manager.

### Configuration examples

To help you configuring your tools, we provide some examples for the tools,
which we provide as part of our
[Capella Docker images repository](https://github.com/DSD-DBS/capella-dockerimages)

=== "Capella"

    ```yaml
    name: Capella
    integrations:
        t4c: true
        pure_variants: false
        jupyter: false
    resources:
        cpu:
            requests: 0.4
            limits: 2
        memory:
            requests: 1.6Gi
            limits: 6Gi
    environment:
        mapping:
            - from: CAPELLACOLLAB_TOKEN
              to: RMT_PASSWORD
            - from: CAPELLACOLLAB_REQUESTER_USERNAME
              to: T4C_USERNAME
    ```

=== "Papyrus/Eclipse"

    ```yaml
    name: Eclipse/Papyrus
    integrations:
        t4c: false
        pure_variants: false
        jupyter: false
    resources:
        cpu:
            requests: 0.4
            limits: 2
        memory:
            requests: 1.6Gi
            limits: 6Gi
    environment:
        mapping:
            - from: CAPELLACOLLAB_TOKEN
              to: RMT_PASSWORD
    ```

=== "pure::variants"

    ```yaml
    name: pure::variants
    integrations:
        t4c: false
        pure_variants: true
        jupyter: false
    resources:
        cpu:
            requests: 0.4
            limits: 2
        memory:
            requests: 1.6Gi
            limits: 6Gi
    ```

=== "Jupyter"

    ```yaml
    name: Jupyter
    integrations:
        t4c: false
        pure_variants: false
        jupyter: true
    resources:
        cpu:
            requests: 1
            limits: 2
        memory:
            requests: 500Mi
            limits: 3Gi
    ```
