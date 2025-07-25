<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Model Complexity Badge Integration

## Set up the Complexity Badge

!!! warning

    Please note the following limitations:

    - A file called `model-complexity-badge.svg` has to exist in the repository.
      We provide a GitLab CI template and a GitHub action to generate the file. Find more information below.
    - Only project administrators can set up the model complexity badge. In addition, one needs access to the Git repository of the model.

1.  To set up the model complexity badge, you need to add the Git API URL to
    your Git instance. More information
    [here](../../../admin/settings/model-sources/git.md).
1.  Link a Git repository to the model, for which you'd like to see the model
    complexity badge.

    !!! info

        If the GitHub repository is public, no token is required for the model complexity badge.
        For private GitHub repositories and for GitLab repositories the model complexity badge integration uses the credentials,
        which are assigned during linking the Git repository.

        - GitLab: Limit the scope of the used token, only scope `read_api` is required.
        - GitHub: If you are using a fine-grained personal access token, add the repository permission for the scope "content" with access `Read-only`.

1.  Follow the CI template instructions
    - [GitLab](https://github.com/DSD-DBS/py-capellambse/tree/master/ci-templates/gitlab#model-badge)
    - [GitHub](https://github.com/DSD-DBS/py-capellambse/tree/master/ci-templates/github#model-badge)

    to add the complexity badge pipeline to the linked repository.

## View the Model Complexity Badge

The model complexity badge is visible in the model overview in the project
details:

![Model complexity badge](./complexity_badge.png){:style="width:400px"}
