<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Manage Git instances

With Git instances, administrators can restrict the location of Git
repositories.

## No Git instance defined

When you don't want to define Git instances, users can use any location for
their repositories. Some features, which require a specific instance, e.g.,
Gitlab, are not available.

## Define a Git instance

1. Please navigate to `Profile` > `Settings`
1. Select `Git` below `Model sources`
1. You can see all existing instances (if any). To add a new integration,
   please use the form below "Add new integration". You have to enter the
   following information:
   <!-- prettier-ignore -->
    1. **Git Type**
        - **General**: Works with every [Git server](https://git-scm.com/book/en/v2/Git-on-the-Server-Setting-Up-the-Server) that supports the Git protocol. Features like the diagram cache are not available.
        - **Gitlab**: Only works with [Gitlab](https://about.gitlab.com/) instances (self-hosted / SaaS). With Gitlab, the diagram cache integration can be used.
    1. **Name**: Any name to identify the instance
    1. **Instance base URL**: The base URL of the instance, e.g., `https://gitlab.com`. For more information, see [Matching between models and instances](#matching-between-models-and-instances)
    1. **API URL (only for type Gitlab)**: The API URL to the [Gitlab REST API](https://docs.gitlab.com/ee/api/rest/). In most of the cases: `{base_url}/api/v4`, e.g., `https://gitlab.com/api/v4`

<!-- prettier-ignore -->
!!! warning
    New repositories have to match at least one instance. Otherwise,
    they can not be added as model source to models.

## Matching between models and instances

Models are matched with instances with a longest prefix match of the URL.

Let's construct a short example. We have two Git instances:

- Instance one with the URL `https://git.example.com/`
- Instance two with the URL `https://git.example.com/test`

A model with the path `https://git.example.com/test/test2.git` is now
associated with instance two. A model with the path
`https://git.example.com/test2/test2.git` would be associated with instance
one.
