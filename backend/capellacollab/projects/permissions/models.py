# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.core.database import decorator as database_decorator
from capellacollab.permissions import models as permissions_models

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.users.tokens.models import DatabaseUserToken


class ProjectUserScopes(core_pydantic.BaseModel):
    root: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Project",
        description="Add capability to delete the project or update the project metadata (visibility & project type & archiving)",
    )
    pipelines: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Pipelines",
        description="See pipelines, create new pipelines or delete existing pipelines",
    )
    pipeline_runs: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.CREATE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Pipeline Runs",
        description="Allow access to see or trigger pipeline runs",
    )
    diagram_cache: set[t.Literal[permissions_models.UserTokenVerb.GET]] = (
        pydantic.Field(
            default_factory=set,
            title="Diagrams from the cache",
            description="Fetch diagrams via the diagram cache API",
        )
    )
    t4c_model_links: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Linked TeamForCapella repositories",
        description="See links to TeamForCapella repositories",
    )
    git_model_links: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Linked Git repositories",
        description="Manage links to Git repositories",
    )
    tool_models: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Tool Models",
        description=(
            "Manage tool models"
            " (UPDATE = Update description, version, nature and order of tool model)"
        ),
    )
    used_tools: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Used Tools",
        description="Configure used tools in the project",
    )
    project_users: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Project Users",
        description=(
            "Manage project users"
            " UPDATE/CREATE can also be used to update roles / escalate own privileges. Use with caution!"
        ),
    )
    access_log: set[t.Literal[permissions_models.UserTokenVerb.GET]] = (
        pydantic.Field(
            default_factory=set,
            title="Project Users Access Log",
            description="Access log of project users",
        )
    )
    provisioning: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Provisioning",
        description=(
            "Access to provisioned and read-only sessions"
            " (includes access to the content of linked Git repositories)"
        ),
    )
    t4c_access: set[t.Literal[permissions_models.UserTokenVerb.UPDATE]] = (
        pydantic.Field(
            default_factory=set,
            title="Access to linked TeamForCapella repositories",
            description=(
                "Access to TeamForCapella repositories in persistent sessions"
                " (Session token will created with GET access)"
            ),
        )
    )
    restrictions: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Model Restrictions",
        description=(
            "Manage restrictions on models (Provide access to pure::variants)"
        ),
    )
    shared_volumes: set[
        t.Literal[
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.CREATE,
            permissions_models.UserTokenVerb.DELETE,
        ]
    ] = pydantic.Field(
        default_factory=set,
        title="Shared Workspaces",
        description=(
            "Access to shared project volumes."
            " GET will provide read-only access,"
            " UPDATE will provide read & write access,"
            " CREATE will provide the ability to create a new shared volume,"
            " DELETE will provide the ability to delete shared volumes."
        ),
    )

    def __and__(self: t.Self, other: "ProjectUserScopes"):
        if not isinstance(other, ProjectUserScopes):
            raise TypeError(
                f"unsupported operand type(s) for &: '{type(self)}' and '{type(other)}'"
            )
        derived_scope = self.model_dump()
        for attribute, verbs in other:
            derived_scope[attribute] &= verbs
        return self.model_validate(derived_scope)

    def __or__(self: t.Self, other: "ProjectUserScopes"):
        if not isinstance(other, ProjectUserScopes):
            raise TypeError(
                f"unsupported operand type(s) for |: '{type(self)}' and '{type(other)}'"
            )
        derived_scope = self.model_dump()
        for attribute, verbs in other:
            derived_scope[attribute] |= verbs
        return self.model_validate(derived_scope)


class DatabaseProjectPATAssociation(database.Base):
    __tablename__ = "project_pat_association"

    token_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("basic_auth_token.id"),
        primary_key=True,
        init=False,
    )
    token: orm.Mapped["DatabaseUserToken"] = orm.relationship(
        back_populates="project_scopes",
    )

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), primary_key=True, init=False
    )
    project: orm.Mapped["DatabaseProject"] = orm.relationship(
        back_populates="tokens",
    )

    scope: orm.Mapped[ProjectUserScopes] = orm.mapped_column(
        database_decorator.PydanticDecorator(ProjectUserScopes),
    )
