<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Introduction

Welcome onboard of the Modeling Collaboration Manager. This platform helps you co-work on architectures using tools like [Capella](https://www.eclipse.org/capella/).

This platform wraps the modeling tools like Capella to create an environment where users can work directly in the project context without having to install or configure the tool. It also takes care of housekeeping for the modeling projects themselves. For example, [TeamForCapella](https://www.obeosoft.com/en/team-for-capella) projects are automatically backed up to git (configuration management).

## Ways of co-working on a Modeling Project

In the context of Capella the platform supports 2 main ways of co-working:

 - **Git-only** - the modeling team uses a git repository to work on the model. The team may use git branches to work on features or capabilities in parallel and a main branch is used for integration and release-tagging. This way of working gives the modeling leads / change control board great control over what contents make it to the model that is used for releases (of things like design documentation). On the downside this co-working method is fairly complicated and requires skilled modeling leadership for challenges like merge conflict resolution and fragmentation management (a way to break up model into smaller files to reduce density of merge conflicts).
 - **Git + TeamForCapella** - with this approach the modeling team can co-work with a very high degree of concurrency and stay away from the difficulties of merge conflict resolution. On the downside it is much harder to control what makes it into the model as there is no barrier except for maybe a modeling process that would stop a person from making changes that are not allowed. Yet there are a few ways around that limitation. For teams with basic or no experience in modeling and git this is probably the best way to start co-woking. Git is still used for nightly backup of the model and release-tagging.

    !!! info "Info: TeamForCapella license required"

        For this co-working method to be enabled you need a valid TeamForCapella license and TeamForCapella server installed and integrated with Collab-Manager.

## Automations and model-derived products

As you can see, git is quite in the middle of the modeling lifecycle. We also use its automation means (pre and post-commit handlers, CI/CD) to automate a number of housekeeping activities:

- Automated model-modifications: this includes range of services like human-friendly element ID assignment, change control and versioning of elements, hyperlinked object title update in descriptions, maintenance of model-derived requirements (req-bot).
- Derived product generation and distribution: generation and publication of model-derived documents and other artifacts (like software interfaces, configurations); caching of diagrams for faster display in linked pages and web-viewer; computation of model metrics for modeling progress dashboards; creation of a human-friendly change summary; spell-checking; synchronization with tools like [Simulink](https://mathworks.com/products/simulink.html), [Polarion](https://polarion.plm.automation.siemens.com/), [Codebeamer](https://codebeamer.com/), [Confluence](https://www.atlassian.com/software/confluence) or even [Grafana](https://grafana.com/).

At this moment Collaboration Manager doesn't provide you with a self-service to configure any of these automations, however since now you know these are possible - you may get in touch with your Systems Engineering Toolchain contact to get these configured.

Now that you have some understanding of the modeling setup and ways of working we can look into how you can actually work in this environment.


## Working with Capella in Collaboration Manager

Capella is not a web native tool, however it runs on Linux - so we can use open-source technologies to deliver it to you via browser. We constructed a [Docker container with Capella](https://github.com/DSD-DBS/capella-dockerimages) and all the plugins you may need, added [Xrdp](http://xrdp.org/) to allow remote connection and [Apache Guacamole](https://guacamole.apache.org/) to stream that connection to your browser. We call instances of those containers **Sessions**. To make this platform scalable and allow people co-work comfortable we use [Kubernetes](https://kubernetes.io/) to run the **Session** containers - which in Kubernetes terms are called **Pod**s. Collaboration Manager uses Kubernetes to start Sessions. Kubernetes is able to scale the cluster to accomodate the active sessions, making it run at reasonable costs in both public and private cloud environments (but of course one could run it in a VM).

There are currently 2 session types supported:

* **Read-only session** - in this case Collaboration Manager gets the latest (or user-selected) model version from git and places that into a read-only workspace within Capella. You can "play" with that model and even make changes, however these changes will not be saved and so will do no harm (for instance to agreed / approved contents). When the session is closed the contents of the workspace is gone.
* **Persistent workspace** - in this mode a user-specific persistent volume is mounted to the Session pod and linked to Capella as the workspace. This enables you to work on projects locally, via git or TeamForCapella as persistent workspace keeps "state" even after the session is closed.


## User Roles

There are 3 roles you can have in a project context:

- **User - read-only** - you can view model snapshots (latest model, any specific release, branch or commit) from git. You may edit the model however your changes will not be saved. (Makes it also useful for training exercises.)
- **User - read/write** - you start a **Persistent Workspace Session**. Your user account is allowed to clone and commit to a git project — if the project co-working model is git-only — or allowed to connect to a remote repository in a TeamForCapella-based project. Also in this mode you may have many co-working projects open at the same time, given that you have a role in those projects that allows this kind of access.
- **Model manager** - can do same as both users above but also can invite or remove users from the managed projects and control their access rights.

You can find more details about [how to request a session here](sessions/request.md).

You may also [learn more about the roles model here](projects/roles.md).

## Next steps

If you like to start a new project and work on it via Collab Manager - please get in touch with one of your tool admins: there is no self-service in this version.
Admins may follow the [project onboarding guideline](projects/new.md) to prepare your project.

To work with the application, you need access to a project. If you don't have it yet or can't find the project you need see [how do I get access to a project](projects/access.md).

At this point you may want to continue to one of the detailed getting-started sections:

- [General introduction to Capella and first steps](getting-started/capella-intro.md)
- [Getting started with a read-only session](getting-started/read-only.md)
- [Getting started with a TeamForCapella-based project](getting-started/read-write-t4c.md)
- Getting started with a git-only project (not yet documented, contact your toolchain team for onboarding)

## Missing information / need support

!!! warning "Important"

    the below is only valid for content-agnostic issues, do not share any proprietary / project related data or real content in reported issues or screenshots.

If you don't find answer to your question on this documentation site please consider opening an [issue on Github](https://github.com/DSD-DBS/capella-collab-manager/issues) or extending the documentation with your own contribution via a [pull request](https://github.com/DSD-DBS/capella-collab-manager/pulls).
