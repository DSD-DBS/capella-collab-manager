<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Kubernetes Deployment (Gitlab CI/CD)

The Kubernetes deploy template is used to deploy the Capella Collaboration
Manager to a Kubernetes cluster using Helm.

Please add the following section to your `.gitlab-ci.yml`:

```yaml
include:
    - remote: https://raw.githubusercontent.com/DSD-DBS/capella-collab-manager/${CAPELLA_COLLABORATION_MANAGER_REVISION}/ci-templates/gitlab/k8s-deploy.yml
```

You have to add the following environment variables on repository level. Make
sure to enable the "Expand variable reference" flag.

-   `PRIVATE_GPG_PATH`: Path to the private GPG key used to decrypt the
    `secret.k8s.json` files.
-   `GRAFANA_HELM_CHART`: (Optional) - This variable is used to set the URL for
    the Grafana Helm chart. It is useful if your deployment environment has
    limited access, so you can specify a URL that is accessible for you.

## SOPS configuration

We make use of [SOPS](https://github.com/getsops/sops) files to store secrets
used in the deployment template.

Create a file `.sops.yaml` at the root level of the repository with the
following structure:

```yaml
creation_rules:
    - path_regex: .*
      encrypted_regex: ^(password|secret|adminPassword|uri|token)
      key_groups:
          - pgp:
                - <GPG fingerprint>
```

Ensure that the GPG fingerprint of the Gitlab runner is present in the
`.sops.yaml` such that it can decrypt the file.

---

Create a file to store the Kubernetes configuration:

```zsh
sops edit ./$TARGET/secret.k8s.json
```

The file has to contain the following content:

```json
{
    "server": "<k8s server>",
    "namespace": "<namespace>",
    "release": "<release>",
    "username": "<username>",
    "token": "<unencrypted token>"
}
```

---

Another configuration file is the encrypted `values.yaml`. In this file you can
overwrite values from the
[default `values.yaml`](https://github.com/DSD-DBS/capella-collab-manager/blob/main/helm/values.yaml).

Create the file with:

```zsh
sops edit ./$TARGET/values.yaml
```

## Gitlab Repository Tree

The tree inside of your Gitlab repository should look like:

```zsh
├── .gitlab-ci.yml
├── .sops.yaml
├── target1
│   ├── values.yaml
│   ├── secret.docker.json
│   └── secret.k8s.json
├── target2
│   ├── values.yaml
│   ├── secret.docker.json
│   └── secret.k8s.json
└── ...
```

This is the (minimal) configuration. For more advanced configuration options,
please refer to the
[k8s-deploy](https://github.com/DSD-DBS/capella-collab-manager/blob/main/ci-templates/gitlab/k8s-deploy.yml)
Gitlab template.
