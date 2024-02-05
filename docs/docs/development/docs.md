<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Documentation

It's important to have a good and up to date documentation for the
Collaboration Manager. Documentation is an accessible way to share knowledge
for developers, administrators and users. It can also be used by support teams
to resolve issues more efficiently.

## Development Setup

Navigate to the `docs` folder from the command line. Executing the command
`make install` followed by `make serve` will build and host the documentation
for viewing locally in a browser at <http://127.0.0.1:8081/>. This live preview
of the documentation automatically refreshes to reflect any changes made to its
source files until the `make serve` process is terminated.

## Style guide

### Titles

When writing the documentation we are using title case in the
[`Chicago Manual of Style`](https://en.wikipedia.org/wiki/Title_case#Chicago_Manual_of_Style).
In addition personal names/ names of packages are written according to their
documentation.

### Cross-linking between pages

When referencing other pages in the documentation, use relative links to the
corresponding `.md` file. `MkDocs` will resolve the link.

!!! warning

    Do not use absolute links to other `.md` files in the same documentation,
    those will break the links when the documentation is built.

### Move documentation files

When moving documentation files, add a redirect from the old location to the
new location. This will prevent any pre-existing links still pointing to the
old direction from breaking. This can be done by adding a line to the
`mkdocs.yml` file:

```yaml
plugins:
  - redirects:
      redirect_maps:
        'path/to/old/template.md': 'path/to/new/template.md' # Reason for the move
```

### Tree structure

The documentation is split into four main sections, each with its own
subsections:

<table>
    <tr>
        <th>Path</th>
        <th>Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><b>/user</b></td>
        <td>User documentation</td>
        <td>
            For users of the Collaboration Manager. It contains information about how to use the platform and its features.
            The content should be written in a way that it is understandable for non-technical users.
        </td>
    </tr>
    <tr>
        <td>/user/project</td>
        <td>Project documentation</td>
        <td>
            This section shall describe how to create, update and delete projects. It also contains information about the project settings and the project access management, as well as backup pipelines, tool models, diagram cache model sources and the model complexity badge.
        </td>
    </tr>
    <tr>
        <td>/user/sessions</td>
        <td>Sessions documentation</td>
        <td>
            Describes tool-independent session features. It contains information how to create persistent and read-only sessions.
        </td>
    </tr>
    <tr>
        <td>/user/tools</td>
        <td>Tools documentation</td>
        <td>
            Tool-specific content belongs here. Examples include Capella-related topics such as workflows for TeamForCapella and Git.
            Jupyter, Papyrus and `pure::variants` configurations should also be documented here. <br \> <br \>
        </td>
    </tr>
    <tr>
        <td><b>/api</b></td>
        <td>API documentation</td>
        <td>
            This section describes the external Collaboration Manager API usage.
        </td>
    </tr>
    <tr>
        <td><b>/admin</b></td>
        <td>Administrator documentation</td>
        <td>For System administrators and businesses, who are interested in administering their own instances.</td>
    </tr>
    <tr>
        <td><b>/development</b></td>
        <td>Development documentation</td>
        <td>For developers who want to contribute to the Collaboration Manager. It contains information about the development setup, the architecture and the code style.</td>
    </tr>

</table>
