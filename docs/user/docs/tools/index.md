<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Tools management

Collab Manager proposing Remote Desktop Protocol server instances and Git synchronisation, it could fit any tool and not
only Capella, provided that there is a Docker image for this tool. That’s why Collab Manager provides an interface to
manipulate Tools.

## What is a Tool

A Tool is any software that allows to work on projects. Capella Collab allow to set for a Tool several Versions and
Natures. In the case of Capella, versions are _5.0_, _5.2_, _6.0_, and natures are _model_ and _library_.
The software is given as a Docker image template, with the version as a variable to get a Docker image.
