<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Introduction

Welcome onboard of the Capella Collaboration Manager. This platform helps you
co-work on architectures using tools like
[Capella](https://www.eclipse.org/capella/),
[Papyrus](https://www.eclipse.org/papyrus/),
[pure::variants](https://www.pure-systems.com/purevariants) and
[Jupyter](https://jupyter.org/) in combination with
[py-capellambse](https://github.com/DSD-DBS/py-capellambse).

This platform wraps the modeling tools to create an environment where users can
can work directly in the project context without having to install or configure
the tool. It also takes care of the housekeeping of the modeling projects
themselves. And that's not all: We also offer project access management and
since the site is completely responsive it is also usable on smartphones.

## Automations and Model-derived Products

Git is quite in the middle of the modeling lifecycle. We also use its
automation means (CI/CD) to automate a number of housekeeping activities:

- Automated model-modifications: This includes range of services like
  human-friendly element ID assignment, change control and versioning of
  elements, hyperlinked object title update in descriptions and maintenance of
  model-derived requirements (req-bot).
- Derived product generation and distribution: generation and publication of
  model-derived documents and other artifacts (like software interfaces,
  configurations); caching of diagrams for faster display in linked pages and
  web-viewer; computation of model metrics for modeling progress dashboards;
  spell-checking; synchronization with tools like
  [Simulink](https://mathworks.com/products/simulink.html),
  [Polarion](https://polarion.plm.automation.siemens.com/),
  [Codebeamer](https://codebeamer.com/),
  [Confluence](https://www.atlassian.com/software/confluence) or even
  [Grafana](https://grafana.com/).

At this moment Collaboration Manager doesn't provide you with a self-service to
configure any of these automations, however since now you know these are
possible - you may get in touch with your Systems Engineering Toolchain contact
to get these configured.

Now that you have some understanding of the modeling setup and ways of working
we can look into how you can actually work in this environment.

## Working with Capella in the Collaboration Manager

Capella is not a web native tool, however it runs on Linux - so we can use
open-source technologies to deliver it to you via browser. We constructed a
[Docker container with Capella](https://github.com/DSD-DBS/capella-dockerimages)
and all the plugins you may need, added [Xrdp](http://xrdp.org/) to allow
remote connection and [Apache Guacamole](https://guacamole.apache.org/) to
stream that connection to your browser. We call instances of those containers
**Sessions**. To make this platform scalable and allow people co-work
comfortably we use [Kubernetes](https://kubernetes.io/) to run the **Session**
containers - which in Kubernetes terms are called **Pod**s. Kubernetes is able
to scale the cluster to accomodate the active sessions, making it run at
reasonable costs in both public and private cloud environments (but of course
one could run it in a VM).

There are currently 2 session types supported:

- **Read-only session** - in this case Collaboration Manager gets the latest
  (or user-selected) model version from git and places that into a read-only
  workspace within Capella. You can "play" with that model and even make
  changes, however these changes will not be saved and so will do no harm (for
  instance to agreed / approved contents). When the session is closed the
  contents of the workspace is gone.
- **Persistent workspace** - in this mode a user-specific persistent volume is
  mounted to the Session pod and linked to Capella as the workspace. This
  enables you to work on projects locally, via git or TeamForCapella as
  persistent workspace keeps "state" even after the session is closed.

We do currently support two different working modes: `TeamForCapella` and
`Git`. If you want to get more information about it, we have prepared a
comparison here:
[Ways of co-working on a Capella project](./tools/capella/t4c-git-compare.md)

## User Roles

There are 3 roles you can have in a project context:

- **User - read-only** - you can view model snapshots (latest model, any
  specific release, branch or commit) from git. You may edit the model however
  your changes will not be saved. (Makes it also useful for training
  exercises.)
- **User - read/write** - you start a **Persistent Workspace Session**. Your
  user account is allowed to clone and commit to a git project — if the project
  co-working model is git-only — or allowed to connect to a remote repository
  in a TeamForCapella-based project. Also in this mode you may have many
  co-working projects open at the same time, given that you have a role in
  those projects that allows this kind of access.
- **Model manager** - can do same as both users above but also can invite or
  remove users from the managed projects and control their access rights.

You may also [learn more about the roles model here](projects/roles.md).

## Next Steps

If you like to start a new project and work on it via Collab Manager - please
follow this guide: [project onboarding guideline](projects/create.md) to
prepare your project. If you want to use the TeamForCapella workflow, please
contact your administrator. Linking models to TeamForCapella repositories can
only be done by administrators.

To work with the application, you need access to a project. If you don't have
it yet or can't find the project you need see
[how do I get access to a project](projects/access.md).

At this point you may want to continue to one of the detailed getting-started
sections:

- [General introduction to Capella and first steps](tools/capella/introduction.md)
- [Getting started with a read-only session](sessions/types/read-only.md)
- [Getting started with a TeamForCapella-based project](sessions/types/persistent.md)
- Getting started with a git-only project (not yet documented, contact your
  toolchain team for onboarding)

## Missing Information / Need Support

!!! warning "Important"

    The below is only valid for content-agnostic issues, do not share any
    proprietary / project related data or real content in reported issues or screenshots.

If you don't find answer to your question on this documentation site please
consider opening an
[issue on Github](https://github.com/DSD-DBS/capella-collab-manager/issues) or
extending the documentation with your own contribution via a
[pull request](https://github.com/DSD-DBS/capella-collab-manager/pulls).
