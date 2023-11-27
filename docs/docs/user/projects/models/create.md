<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Create a _Collaboration Manager_ Model

We offer a guided process to create models in a project. To create a model, you
have to be at least [project lead](../../projects/roles.md). If you're coming
from project creation, you're ready to go. Otherwise, please navigate to the
_Projects_ tab of the navigation bar, open the project in which you want to
create a model, and click on the “+” icon.

The creation can be interrupted at any step, however an unfinished model will
lack some essential features, so it’s recommended to go through the whole
process.

## Step 1: Create Model

This page allows to set a project name, description, and a tool. The name and
tool are required. The tool can be changed after the model creation.

## Step 2: Choose Primary Source

On this page, you can select the type of source. Right now, we offer the
following options:

1. Link an existing **Git** repository. For this option, you don't need
   additional support.
1. Create a new **Git** repository. This option is not supported yet. Please
   create the repository yourself and continue with the first option.
1. Link a **TeamForCapella** repository. Only available for the `Capella` tool.
   If you're project lead and not administrator, you are not able to select
   this option. You'll need assistance by an administrator. You can abort the
   process here and continue with the help of an administrator later on.
1. Create a **TeamForCapella** repository. Only available for the `Capella`
   tool. If you're project lead and not administrator, you are not able to
   select this option. You'll need assistance by an administrator. You can
   abort the process here and continue with the help of an administrator later
   on.

## Step 3: Add Source

If you chose option 1 or 2 in the last step, please read the
`Link existing Git repository` part of this step. If you chose option 3 or 4,
you can should read the `Link existing T4C repository` part.

### Step 3.1 Link Existing Git Repository

It is important for this step to have an existing Git repository which is
reachable from inside your environment.

You have to enter the following information:

<!-- prettier-ignore-start -->

1. **Instance**: If your environment restricts the usage of Git instances, you
   have to select your instance here. Otherwise, you can continue with the next
   step.
1. **URL**: Please enter the URL of your Git repository here. All URLs accepted
   by the [`git clone`](https://git-scm.com/docs/git-clone) are also accepted
   in the UI.

    !!! info
        If your environment restricts the usage of instances, make sure to match
        the given prefix. You can also enter `Relative URLs`. In this case,
        you can see the resulting URL after the `info`-icon.

1. **Username** and **password/token**: Please enter your username and token
   here, which is needed to access the repository. Please note that we don't
   have support for SSH authentication yet.

   - For public repositories: You don't need to enter credentials. However,
     backups will need credentials to be able to push to the repository.
   - For private repositories: You need to enter credentials for read-only
     sessions and backups.

    !!! danger
        The credentials are stored in the database, and even if not accessible
        from outside, they are stored in plain text, so the password
        of the user should not be used. Rather use a token.

    !!! warning
        The credentials should be scoped and should only work for the required
        repository. When changing the repository URL and the credentials are not
        changed, other project leads can gain access to different repositories
        with your token.

<!-- prettier-ignore-end -->

### Step 3.2 Link Existing T4C Repository

<!-- prettier-ignore -->
!!! warning
    This step can only be executed by administrators

The TeamForCapella instance has to exist before we can continue. Please select
the TeamForCapella instance and the TeamForCapella repository. With `project`,
you can specify the name of the model in Capella. We recommend using the same
name for the repository and project.

## Step 4: Metadata

This is an important step.

Here, you can select the version and the model nature of your tool. If you
don't select any version, the functionality will be restricted. You will not be
able to setup backups or create read-only sessions.

If suitable for your project, select one of the latest versions of Capella.
Older versions may be removed in the future. Make sure your model is up to date
and in case you update it in time.
