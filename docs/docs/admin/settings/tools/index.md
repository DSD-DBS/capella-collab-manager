<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Tools Management

Tools are a central element of the Collaboration Manager. While Capella remains
a core tool of the platform, we have generic tool support. This not only allows
administrators to use additional tools such as Eclipse, pure::variants or
Papyrus, but also to expand the platform with their own tools.

A tool can be added if it can run in a Docker container and can be reached via
RDP. General web-based tool support is on our roadmap; currently only Jupyter
can be used as a web-based tool.

Tools can be found in various places on the platform:

- Models in projects are always assigned to a specific tool.
- Sessions are always started for a specific tool.

Each tool has different versions and natures, which can be configured
individually. Since different versions can be enabled in parallel, it helps to
carry out complex migrations step by step.

## Managing Tools

Tools are managed by the platform administrator. The tools management page
allows the administrator to add, edit, and delete tools.

The tool management page can be found at `Menu` > `Settings` > `Tools`. Here,
you'll find several YAML editors.

To change the configuration, edit the YAML configuration in the corresponding
editor. Once you're done, click `Save`. We run several validation rules during
saving to avoid configuration errors. You'll be notified about the save result
in the bottom left corner via a notification.

The `id` entry is only displayed for reference and cannot be changed, any
changes of the `id` are ignored. When creating a new version or a new nature,
the ID will be auto-assigned.

To see all available options, please refer to the API documentation. A link to
the corresponding route of the API documentation is provided on the tools
management page.
