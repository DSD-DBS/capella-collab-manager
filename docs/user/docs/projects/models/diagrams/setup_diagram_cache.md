<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Set up the diagram cache integration

!!! warning

    Please note the following limitations:

       - The diagram cache is only available for your own Gitlab and Github projects. You can not use it if you have no permissions for a Github repository even though the pipeline might be up to date and the project is public.
       - You need a pipeline in the Git repository of the model, which serves the
      diagrams via
      [job artifacts Gitlab](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html) or [job artifacts Github](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts) (see also limitations for private repositories).
      The job has to be called `update_capella_diagram_cache` and has to generate the following files:
        - `diagram_cache/index.json`
        - `diagram_cache/{uuid}.svg` for each diagram
    - One pipeline in the linked Git repository should not contain more than 20 jobs.

1. To set up the diagram cache, you need to add the Git API URL to your Gitlab
   instance. More information [here](../../../settings/model-sources/git.md)
1. Link a Git repository to the model, for which you'd like to see the diagram
   cache.
   <!-- prettier-ignore -->
    !!! info
         The diagram cache integration uses the credentials, which are assigned when
         creating the Git model integration. Limit the scopes of the used token, only
         scope `read_api` (Gitlab) and `read-only` for the "actions" scope of the repository permissions (Github, Personal Access Token) is required.

1. Follow the
   [Gitlab CI template instructions](https://github.com/DSD-DBS/capella-dockerimages/tree/main/ci-templates/gitlab#diagram-cache)
   to add the diagram cache pipeline to the `.gitlab-ci.yml` of the linked
   repository.
1. You're ready to go. Validate if the setup works:
   [View the diagrams](./view_diagram_cache.md)
