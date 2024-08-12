<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Image Builder (Gitlab CI/CD)

The image builder template builds the images and pushes them to any Docker
registry.

Please add the following section to your `.gitlab-ci.yml`:

```yaml
include:
    - remote: https://raw.githubusercontent.com/DSD-DBS/capella-collab-manager/${CAPELLA_COLLABORATION_MANAGER_REVISION}/ci-templates/gitlab/image-builder.yml
```

The build images are tagged with the revision they were build with (e.g., when
running for main the tag would be `:main`). All characters matching the regex
[^a-za-z0-9.] will be replaced with -.

You have to add the following environment variables on repository level. Make
sure to enable the "Expand variable reference" flag.

-   `PRIVATE_GPG_PATH`: Path to the private GPG key used to decrypt the
    `secret.docker.json` file (More about this file [below](#docker-sops-file))
-   Variables specifying how to name each image:
    -   `FRONTEND_IMAGE_NAME` (defaults to `capella/collab/frontend`)
    -   `BACKEND_IMAGE_NAME` (default to `capella/collab/backend`)
    -   `DOCS_IMAGE_NAME` (defaults to `capella/collab/docs`)
    -   `GUACAMOLE_IMAGE_NAME` (defaults to `capella/collab/guacamole`)

This is the (minimal) configuration. For more advanced configuration options,
please refer to the
[image-builder](https://github.com/DSD-DBS/capella-collab-manager/blob/main/ci-templates/gitlab/image-builder.yml)
Gitlab template.

### Docker SOPS File

We make use of [SOPS](https://github.com/getsops/sops) files to store secrets
used in the image builder template.

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

You need to have a directory `$TARGET` for each target with a
`secret.docker.json` inside. You can create the `secret.docker.json` by running
the following command:

```zsh
sops edit ./$TARGET/secret.docker.json
```

Then, enter the following content:

```json
{
    "registry": "<registry>",
    "username": "<username>",
    "password": "<password>"
}
```

Verify that you can open the secret file with
`sops ./<target>/secret.docker.json`.
