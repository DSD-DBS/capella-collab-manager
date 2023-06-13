<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Gitlab CI templates

Currently, we provide the following Gitlab CI/CD templates:

- [Image builder](#image-builder): Build and push backend, frontend, docs and guacamole Docker images to any Docker registry.
- [Kubernetes deploy](#kubernetes-deploy): Deploy to a Kubernetes environment using helm

## Image builder

The image builder template builds the following images and pushes them to any Docker registry:

- backend
- frontend
- user documentation
- guacamole

Please add the following section to your `.gitlab-ci.yml`:

```yml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-collab-manager/${CAPELLA_COLLABORATION_MANAGER_REVISION}/ci-templates/gitlab/image-builder.yml
```

The build images are tagged with the revision they were build with
(e.g., when running for main the tag would be `:main`)
All characters matching the regex [^a-za-z0-9.] will be replaced with -.

You have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `PRIVATE_GPG_PATH`: Path to the private GPG key used to decrypt the
  `secret.docker.json` file (More about this file [below](#docker-sops-file))
- Variables speciying how to name each image:
  - `FRONTEND_IMAGE_NAME` (defaults to _capella/collab/frontend_)
  - `BACKEND_IMAGE_NAME` (default to _capella/collab/backend_)
  - `DOCS_IMAGE_NAME` (defaults to _capella/collab/docs_)
  - `GUACAMOLE_IMAGE_NAME` (defaults to _capella/collab/guacamole_)

In addition you can adjust the following variables when running a pipeline:

- Variables specifying whether to build an image (default to 1):
  - `FRONTEND`: Build the frontend image?
  - `BACKEND`: Build the backend image?
  - `DOCS`: Build the docs image?
  - `GUACAMOLE`: Build the guacamole image?
- `TARGET`: The target for which you want to build the images
  (More information why this is important [below](#docker-sops-file))

### Docker SOPS file

We make use of [Mozilla SOPS](https://github.com/mozilla/sops) files to store
secrets used in the image builder template. Therefore you need to have a
directory `$TARGET` for each target with a `secret.docker.json` inside.
You can create the `secret.docker.json` by running the following command:

```zsh
sops -e --output ./<target>/secret.docker.json input.json
```

The `input.json` in this command is a placeholder for your own input file,
which should have the following structure:

```json
{
  "registry_unencrypted": "<registry>",
  "username_unencrypted": "<username>",
  "password": "<unencrypted password>"
}
```

Verify that you can open the secret file with `sops ./<target>/secret.docker.json`.
When it works, delete the `input.json`!

In addition, you will need a `.sops.yaml` at the root level having the
following structure:

```yml
creation_rules:
  - path_regex: .*
    key_groups:
      - pgp:
          - <GPG fingerprint>
```

Any time you update the `.sops.yaml` (i.e., adding or removing a fingerprint)
you will have to run `sops updatekeys ./<target>/secret.docker.json` to ensure
that only authorized persons can decrypt the secret file.

Lastly, please ensure that your Gitlab runners GPG fingerprint is present
in the `.sops.yaml` such that it can use the secret values.

## Kubernetes Deploy

The Kubernetes deploy template is used to deploy the Capella Collaboration
Manager to a Kubernetes cluster using Helm.

Please add the following section to your `.gitlab-ci.yml`:

```yml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-collab-manager/${CAPELLA_COLLABORATION_MANAGER_REVISION}/ci-templates/gitlab/k8s-deploy.yml
```

You have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `PRIVATE_GPG_PATH`: Path to the private GPG key used to decrypt the
  `secret.k8s.json` files.
- `GRAFANA_HELM_CHART`: (Optional) - This variable is used to set the URL
  for the Grafana Helm chart. It is useful if your deployment environment
  has limited access, so you can specify a URL that is accessible for you.

In addition you can adjust the following variables when running a pipeline:

- `TARGET`: The target for which you want to build the images
  (More information why this is important [below](#docker-and-kubernetes-sops-files))
- `REVISION`: The revision of the capella collab manager repository you want to use

### Docker and Kubernetes sops files

For the `k8s-deploy.yml` you need to have some secret sops files in place.
First of all, you need a `secret.docker.json` file as described
[here](#docker-sops-file). In addition, you need to have a `secret.k8s.json`
in each target directory created by a json file having the following structure:

```json
{
  "server_unencrypted": "<k8s server>",
  "namespace_unencrypted": "<namespace>",
  "release_unencrypted": "<release>",
  "username_unencrypted": "<username>",
  "token": "<unencrypted token>"
}
```

In addition, you need to have a `general.values.yaml` containing
all the `values.yaml` values that do not have to be encrypted and a
`secret.values.yaml` only containing the values that should be encrypted
(Please do not use YAML anchors in the `secret.values.yaml` file and do not
use the `_unencrypted` suffix in the variable names).

Please delete the plain text files containing secrets directly
after encrypting them.

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

This is the (minimal) configuration (except that you would just need a target
directory). For more advanced configuration options, please refer to the
[image-builder](./image-builder.yml) or [k8s-deploy](k8s-deploy.yml) Gitlab template.
