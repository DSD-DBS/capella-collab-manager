# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import typing as t

import pydantic

from capellacollab.core import pydantic as core_pydantic


class UserTokenVerb(str, enum.Enum):
    GET = "GET"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class UserScopes(core_pydantic.BaseModelStrict):
    sessions: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Sessions",
        description=(
            "Manage sessions of your own user."
            " With the UPDATE permission a session can be shared with another user and files can be modified via the file browser."
        ),
    )
    projects: set[t.Literal[UserTokenVerb.CREATE]] = pydantic.Field(
        default_factory=set,
        title="Projects",
        description="Create new projects",
    )
    tokens: set[
        t.Literal[
            UserTokenVerb.GET, UserTokenVerb.CREATE, UserTokenVerb.DELETE
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Personal Access Tokens",
        description=(
            "Manage Personal Access Tokens."
            " Use with caution!"
            " This permission can be used to escalate privileges by creating tokens with a larger scope."
        ),
    )
    feedback: set[t.Literal[UserTokenVerb.CREATE]] = pydantic.Field(
        default_factory=set,
        title="Feedback",
        description="Submit feedback",
    )


class AdminScopes(core_pydantic.BaseModelStrict):
    users: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Users",
        description=(
            "Manage all users of the application."
            "\nCREATE/UPDATE can be used to change the role of a user / escalate privileges. Use with caution!"
        ),
    )
    projects: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Projects",
        description=(
            "Grant permission to all sub-resources of ALL projects. Use with caution!"
            " If possible, use project scopes instead."
        ),
    )
    tools: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Tools",
        description="Manage all tools, including its versions and natures",
    )
    announcements: set[
        t.Literal[
            UserTokenVerb.CREATE, UserTokenVerb.UPDATE, UserTokenVerb.DELETE
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Announcements",
        description="Manage all announcements",
    )
    monitoring: set[t.Literal[UserTokenVerb.GET]] = pydantic.Field(
        default_factory=set,
        title="Monitoring",
        description="Allow access to monitoring dashboards, Prometheus and Grafana",
    )
    configuration: set[t.Literal[UserTokenVerb.GET, UserTokenVerb.UPDATE]] = (
        pydantic.Field(
            default_factory=set,
            title="Global Configuration",
            description="See and update the global configuration",
        )
    )
    git_servers: set[
        t.Literal[
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Git Server Instances",
        description="Manage links to Git server instances",
    )
    t4c_servers: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="TeamForCapella Servers",
        description="Manage Team4Capella servers and license servers",
    )
    t4c_repositories: set[
        t.Literal[
            UserTokenVerb.GET,
            UserTokenVerb.CREATE,
            UserTokenVerb.UPDATE,
            UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="TeamForCapella Repositories",
        description="Manage Team4Capella repositories",
    )
    pv_configuration: set[
        t.Literal[
            UserTokenVerb.GET, UserTokenVerb.UPDATE, UserTokenVerb.DELETE
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="pure::variants Configuration",
        description="pure::variants license configuration",
    )
    events: set[t.Literal[UserTokenVerb.GET]] = pydantic.Field(
        default_factory=set, title="Events", description="See all events"
    )
    sessions: set[t.Literal[UserTokenVerb.GET]] = pydantic.Field(
        default_factory=set,
        title="Sessions",
        description="See all sessions",
    )
    workspaces: set[t.Literal[UserTokenVerb.GET, UserTokenVerb.DELETE]] = (
        pydantic.Field(
            default_factory=set,
            title="User Workspaces",
            description="See user workspaces",
        )
    )
    personal_access_tokens: set[
        t.Literal[UserTokenVerb.GET, UserTokenVerb.DELETE]
    ] = pydantic.Field(
        default_factory=set,
        title="Personal Access Tokens (Global)",
        description="Get and revoke personal access tokens of ALL users.",
    )
    tags: set[
        t.Literal[
            UserTokenVerb.CREATE, UserTokenVerb.UPDATE, UserTokenVerb.DELETE
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Tags",
        description="Manage the available tags globally",
    )


class GlobalScopes(core_pydantic.BaseModelStrict):
    user: UserScopes = pydantic.Field(
        default=UserScopes(), title="User Scopes"
    )
    admin: AdminScopes = pydantic.Field(
        default=AdminScopes(), title="Administrator Scopes"
    )

    def __and__(self: t.Self, other: "GlobalScopes"):
        if not isinstance(other, GlobalScopes):
            raise TypeError(
                f"unsupported operand type(s) for &: '{type(self)}' and '{type(other)}'"
            )
        derived_scope = self.model_dump()
        for scope_name, scope in other:
            for attribute, verbs in scope:
                derived_scope[scope_name][attribute] &= verbs
        return self.model_validate(derived_scope)

    def __or__(self: t.Self, other: "GlobalScopes"):
        if not isinstance(other, GlobalScopes):
            raise TypeError(
                f"unsupported operand type(s) for |: '{type(self)}' and '{type(other)}'"
            )
        derived_scope = self.model_dump()
        for scope_name, scope in other:
            for attribute, verbs in scope:
                derived_scope[scope_name][attribute] |= verbs
        return self.model_validate(derived_scope)
