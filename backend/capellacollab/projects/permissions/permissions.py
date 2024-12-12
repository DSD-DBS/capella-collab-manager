# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import models as users_models

from . import models


def inherit_global_permissions(
    global_scope: permissions_models.GlobalScopes,
) -> models.ProjectUserScopes:
    """When admin.projects permission is set, inherit the permissions to all projects"""

    scope = models.ProjectUserScopes().model_dump()

    for attribute in scope:
        for verb in global_scope.admin.projects:
            type_annotations = models.ProjectUserScopes.model_fields[  # pylint: disable=unsubscriptable-object
                attribute
            ].annotation
            assert type_annotations

            # Assuming a type of structure set[t.Literal[UserTokenVerb.X, UserTokenVerb.Y]]
            if verb in type_annotations.__args__[0].__args__:
                scope[attribute].add(verb)

    return models.ProjectUserScopes.model_validate(scope)


def derive_project_permissions_from_role(
    project: projects_models.DatabaseProject,
    project_user: projects_users_models.ProjectUserAssociation | None,
    user: users_models.DatabaseUser,
) -> models.ProjectUserScopes:
    read_only_permissions = models.ProjectUserScopes(
        root={permissions_models.UserTokenVerb.GET},
        diagram_cache={permissions_models.UserTokenVerb.GET},
        git_model_links={permissions_models.UserTokenVerb.GET},
        tool_models={permissions_models.UserTokenVerb.GET},
        used_tools={permissions_models.UserTokenVerb.GET},
        provisioning={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.DELETE,
        },
        shared_volumes={
            permissions_models.UserTokenVerb.GET,
        },
    )
    write_permissions = read_only_permissions | models.ProjectUserScopes(
        t4c_access={permissions_models.UserTokenVerb.UPDATE},
        restrictions={permissions_models.UserTokenVerb.GET},
        shared_volumes={
            permissions_models.UserTokenVerb.UPDATE,
        },
    )
    project_lead_permissions = write_permissions | models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        pipelines={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        pipeline_runs={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.CREATE,
        },
        t4c_model_links={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        git_model_links={
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        tool_models={
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        used_tools={
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        project_users={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        access_log={permissions_models.UserTokenVerb.GET},
        restrictions={permissions_models.UserTokenVerb.UPDATE},
    )

    if user.role == users_models.Role.ADMIN:
        return project_lead_permissions

    if project_user:
        if project_user.role == projects_users_models.ProjectUserRole.MANAGER:
            return project_lead_permissions

        if project_user.role == projects_users_models.ProjectUserRole.USER:
            if (
                project_user.permission
                == projects_users_models.ProjectUserPermission.WRITE
            ):
                return write_permissions
            else:
                return read_only_permissions

    if project.visibility == projects_models.ProjectVisibility.INTERNAL:
        return read_only_permissions

    return models.ProjectUserScopes()
