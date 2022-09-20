<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Introduction

Welcome onboard of the Modeling Collaboration Manager. This platform should help you co-working on architectures using tools like [Capella](https://www.eclipse.org/capella/).

This platform wraps the modeling tools like Capella to create an environment where users can work directly in the project context without having to install or configure the tool. It also takes care of housekeeping for the modeling projects themselves - for example, for TeamForCapella projects the platform does a nightly backup to git (configuration management).

## Ways of co-working on a Modeling Project

In the context of Capella the platform supports 2 main ways of co-working:

 - **git-only** - modeling team uses a git repository to work on model. The team may use git features such as branches to work on features or capabilities in parallel and main branch is used for integration and release-tagging. This way of working gives the modeling leads / change control board great control over what contents make it to the model that is used for releases (of things like design documentation). On the downside this co-working method is fairly complicated and requires skilled modeling leadership for challenges like merge conflict resolution and fragmentation management (way to break up model into smaller files to reduce density of merge conflicts).
 - **git + TeamForCapella** - with this approach the modeling team can co-work with a very high degree of concurrency and stay away from the difficulties of merge conflict resolution. On the downside it is much harder to control what makes it into the model as there is no barrier except for maybe a modeling process that would stop a person from making changes that were not allowed. Yet there are a few ways around that limitation. For teams with basic or no experience in modeling and git this is probably the best way to start co-woking. Git is still used for nightly backup of the model and release-tagging.
 
    !!! warning "Warning: TeamForCapella license required"

        for this co-working method to be enabled you need a valid TeamForCapella license and TeamForCapella server installed and integrated with Collab-Manager. 

## Automations and model-derived products

As you can see, git is quite in the middle of the modeling life. We also use its automation means (pre and post-commit handlers, CI/CD kind of thing) to automate a number of housekeeping activities like:

- automated model-modifications: this includes range of services like human-friendly element ID assignment, change control and versioning of elements, hyperlinked object title update in descriptions, maintenance of model-derived requirements (req-bot), etc.
- derived product generation and distribution: generation and publication of model-derived documents and other artifacts (like software interfaces, configurations, etc); caching of diagrams for faster display in linked pages and web-viewer; compute of model metrics update for modeling progress dashboards; compute of human-friendly change summary for the model change history; spell-checking; push of model contents update or by-products to other linked tools like [Simulink](https://mathworks.com/products/simulink.html), [Polarion](https://polarion.plm.automation.siemens.com/), [Codebeamer](https://codebeamer.com/), [Confluence](https://www.atlassian.com/software/confluence) or even [Grafana](https://grafana.com/).

At the moment Collaboration Manager doesn't provide you with a self-service to configure any of these automations, however since now you know these are possible - you may get in touch with your Systems Engineering Toolchain contact to get these configured.

Now that you have some understanding of the modeling setup and ways of working we can look into how you can actually work here.


## Workin with Capella in Collaboration Manager

Capella is not yet a web native tool, however it runs on Linux - so we can use some basic open-source technologies to deliver it to you via browser. We constructed a [Docker container with Capella](https://github.com/DSD-DBS/capella-dockerimages) and all the plugins you may need, added [xrdp](http://xrdp.org/) to allow remote connection to it and [Apache Guacamole](https://guacamole.apache.org/) to stream that connection to your browser. We call instances of those containers **Sessions**. To make this platform scalable and allow multiple people co-work comfortable we use [Kubernetes](https://kubernetes.io/) to run the **Session** containers - which in Kubernetes terms are called **Pod**s. Collaboration Manager controls a Sessions namespace within a Kubernetes cluster to scale it up and down in response to the number of active users making it run scale at reasonable costs in both public and private cloud environments (but of course one could run it in a VM).

Collaboration Manager prepares sessions in response to user request. There are currently 2 session types supported:

* **read-only session** - in this case Collaboration Manager gets the latest (or user-selected) model version from git and places that into a read-only workspace within Capella. You can "play" with that model and even make changes, however these changes will not be saved and so will do no harm (for instance to agreed / approved contents). When the session is closed all the contents of Capella workspace are gone.
* **persistent workspace** - in this mode a user-specific persistent volume is mounted to the Session pod and linked into Capella as the workspace. This enables user to work on projects locally, via git or TeamForCapella as persistent workspace keeps "state" even after the session is closed.


## User Roles

At the moment there are 3 roles you can have in a project context:

- **user - read-only** - you can view model snapshots (latest model, any specific release, branch or commit) from git. You may edit the cloned model however your changes will not be saved (makes it also useful for training exercises)
- **user - read/write** - you can do same as above but also start a **Persistent Workspace Session**. Your user account is allowed to clone and commit to a git project (if the project co-working model is git-only) or allowed to connect to a remote repository in a TeamForCapella-based project. Also in this mode you may have many co-working projects open at the same time, given that you have a role in those projects that allows this kind of access.
- **model manager** - can do same as both users above but also can invite or remove other platform users into the managed projects and control their access rights.

You can find more details about [how to request a session here](sessions/request.md)

The below sections will give you more details re how to get into editing mode depending on the project co-working models.



## Next steps

If you'd like to start a new project and work on it via Collab Manager - please get in touch with one of tool admins, there is no self-service in this version.
Admins may follow the [project onboarding guideline](todo) to prepare your project.

To work with the application, you need access to a project - if you don't have it yet or cant find the project you need see [how do I get access to a project?](projects/access.md).

If you are a member of existing project its co-working method is based on ...

-  TeamForCapella - see [getting started with a TeamForCapella project](getting-started.md#getting-started-with-a-teamforcapella-based-project).
-  git-only - see [getting started with a git-only project](getting-started.md#getting-started-with-a-git-only-project).


## Missing information / need support

!!! warning "Important"

    the below is only valid for content-agnostic issues, do not share any proprietary / project related data or real content in reported issues or screenshots.

If you don't find answer to your question within this documentation site please consider opening an [issue on Github](https://github.com/DSD-DBS/capella-collab-manager/issues) or extending the documentation with your own contribution via a [pull request](https://github.com/DSD-DBS/capella-collab-manager/pulls).
