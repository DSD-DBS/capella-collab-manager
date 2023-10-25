<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Image Builder (Gitlab CI/CD)

The image builder template builds the following images and pushes them to any
Docker registry:

- backend
- frontend
- documentation
- guacamole

Please add the following section to your `.gitlab-ci.yml`:

```yaml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-collab-manager/${CAPELLA_COLLABORATION_MANAGER_REVISION}/ci-templates/gitlab/image-builder.yml
```

The build images are tagged with the revision they were build with (e.g., when
running for main the tag would be `:main`) All characters matching the regex
[^a-za-z0-9.] will be replaced with -.

You have to add the following environment variables on repository level. Make
sure to enable the "Expand variable reference" flag.

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
- `TARGET`: The target for which you want to build the images (More information
  why this is important [below](#docker-sops-file))

This is the (minimal) configuration. For more advanced configuration options,
please refer to the
[image-builder](https://github.com/DSD-DBS/capella-collab-manager/blob/main/ci-templates/gitlab/image-builder.yml)
Gitlab template.

### Docker SOPS File

We make use of [Mozilla SOPS](https://github.com/mozilla/sops) files to store
secrets used in the image builder template. Therefore you need to have a
directory `$TARGET` for each target with a `secret.docker.json` inside. You can
create the `secret.docker.json` by running the following command:

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

Verify that you can open the secret file with
`sops ./<target>/secret.docker.json`. When it works, delete the `input.json`!

In addition, you will need a `.sops.yaml` at the root level having the
following structure:

```yaml
creation_rules:
  - path_regex: .*
    key_groups:
      - pgp:
          - <GPG fingerprint>
```

Any time you update the `.sops.yaml` (i.e., adding or removing a fingerprint)
you will have to run `sops updatekeys ./<target>/secret.docker.json` to ensure
that only authorized persons can decrypt the secret file.

Lastly, please ensure that your Gitlab runners GPG fingerprint is present in
the `.sops.yaml` such that it can use the secret values.
