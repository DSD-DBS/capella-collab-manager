<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Frontend Routes

For consistency, we have a strict structure for our frontend route URIs.
The structure is based on REST, but not completely the same due to the limitations of the unavailable request methods.

- `/resources` for the resource overview, e.g., `/projects` for the projects overview
- `/resources/action` for a specific action (not related to a specific instance of the resource), e.g., `/projects/create` to create a project. Possible actions are:
  - `create`
  - `delete`
  - or any other action if the action is not used to `create` or `delete` a resource.
- `/resources/action/subaction` for a specific action related to a parent action, e.g., `/project/:name/models/create/source` to go to the source stage of the model creation.
- `resource/:name` to access a single instance of type resource.
- `resource/:name/childresource` to access a single child resource of a specific instance from type resource.

## Examples

Valid routes are:

- `/project/test/models/create` is a valid route to create a model in the project `test`.
- `/projects` is a valid route for the overview of projects.

These are not valid:

- `/project/create` (`project` should be plural)
- `/models` (`models` is a child resource of `projects`, therefore it should be `/projects/:id/models`)
