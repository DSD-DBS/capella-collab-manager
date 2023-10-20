<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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

- `PRIVATE_GPG_PATH`: Path to the private GPG key used to decrypt the
  `secret.k8s.json` files.
- `GRAFANA_HELM_CHART`: (Optional) - This variable is used to set the URL for
  the Grafana Helm chart. It is useful if your deployment environment has
  limited access, so you can specify a URL that is accessible for you.

In addition you can adjust the following variables when running a pipeline:

- `TARGET`: The target for which you want to build the images (More information
  why this is important [below](#docker-and-kubernetes-sops-files))
- `REVISION`: The revision of the capella collab manager repository you want to
  use

### Docker and Kubernetes sops files

For the `k8s-deploy.yml` you need to have some secret sops files in place.
First of all, you need a `secret.docker.json` file as described
[here](#docker-sops-file). In addition, you need to have a `secret.k8s.json` in
each target directory created by a json file having the following structure:

```json
{
  "server_unencrypted": "<k8s server>",
  "namespace_unencrypted": "<namespace>",
  "release_unencrypted": "<release>",
  "username_unencrypted": "<username>",
  "token": "<unencrypted token>"
}
```

In addition, you need to have a `general.values.yaml` containing all the
`values.yaml` values that do not have to be encrypted and a
`secret.values.yaml` only containing the values that should be encrypted
(Please do not use YAML anchors in the `secret.values.yaml` file and do not use
the `_unencrypted` suffix in the variable names).

Please delete the plain text files containing secrets directly after encrypting
them.

## Gitlab repository tree

The tree inside of your Gitlab repository should look like:

```zsh
├── .gitlab-ci.yml
├── .sops.yaml
├── environment.prod.ts
├── favicon.ico
├── target1
│   ├── general.values.yaml
│   ├── secret.values.yaml
│   ├── secret.docker.json
│   └── secret.k8s.json
├── target2
│   ├── general.values.yaml
│   ├── secret.values.yaml
│   ├── secret.docker.json
│   └── secret.k8s.json
└── ...
```

This is the (minimal) configuration. For more advanced configuration options,
please refer to the
[k8s-deploy](https://github.com/DSD-DBS/capella-collab-manager/blob/main/ci-templates/gitlab/k8s-deploy.yml)
Gitlab template.
