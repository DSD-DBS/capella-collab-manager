<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!--
SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
SPDX-License-Identifier: Apache-2.0
-->

# Gitlab CI templates

Currently, we provide the following Gitlab CI/CD templates:

- [Image builder](#image-builder): Build and push backend, frontend, docs and guacamole Docker images to any Docker registry.

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

The build images are tagged with `:latest` if built with revision "main".
In addition, all images are tagged with the branch or tag name.
All characters matching the regex [^a-za-z0-9.] will be replaced with -.

You have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `CAPELLA_COLLABORATION_MANAGER_REVISION`: Revision of this Github repository.
- Variables related to the Docker registry (all parameters are passed to `docker login`):
  - `DOCKER_REGISTRY`: The URL to the Docker registry
  - `DOCKER_REGISTRY_USER`: Username of a techuser with push permission to the Docker registry
  - `DOCKER_REGISTRY_PASSWORD`: Corresponding password of the techuser

The tree inside of your Gitlab repository should look like:

```zsh
├── .gitlab-ci.yml
├── environment.prod.ts (check the frontend documentation for more information)
└── favicon.ico (this is used as favicon for the frontend)
```

This is the minimal configuration. For more advanced configuration options,
please refer to the [Gitlab CI template](./image-builder.yml).
