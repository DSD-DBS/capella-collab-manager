<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Development Troubleshooting

## The `k3d` Registry is Unreachable

If the k3d registry is unreachable, i.e. the `make reach-registry` command
fails with errors like "Could not resolve host", `k3d-myregistry.localhost`
isn't resolved properly to `127.0.0.1`. To resolve this, you can try the
following options:

-   On Debian/Ubuntu based systems, you can install nss-myhostname.
    `nss-myhostname` resolves all subdomains of localhost to localhost:

    ```sh
    sudo apt install libnss-myhostname
    ```

-   Add the following line to the `/etc/hosts` on the host machine:
    ```
    127.0.0.1 k3d-myregistry.localhost
    ```

After applying the steps, verify that the registry is reachable by running
`make reach-registry` again.
