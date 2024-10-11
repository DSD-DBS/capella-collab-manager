# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from sqlalchemy import orm

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    injectables as git_injectables,
)
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.provisioning import (
    crud as provisioning_crud,
)
from capellacollab.projects.toolmodels.provisioning import (
    models as provisioning_models,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.settings.modelsources.git import core as instances_git_core
from capellacollab.settings.modelsources.git import (
    exceptions as instances_git_exceptions,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import interface


class ResolvedSessionProvisioning(t.TypedDict):
    entry: sessions_models.SessionProvisioningRequest
    model: toolmodels_models.DatabaseToolModel
    project: projects_models.DatabaseProject
    git_model: git_models.DatabaseGitModel


class ProvisionWorkspaceHook(interface.HookRegistration):
    """Takes care of the provisioning of user workspaces."""

    @classmethod
    async def async_configuration_hook(
        cls,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        max_number_of_models = (
            request.tool.config.provisioning.max_number_of_models
        )
        if (
            max_number_of_models
            and len(request.provisioning) > max_number_of_models
        ):
            raise sessions_exceptions.TooManyModelsRequestedToProvisionError(
                max_number_of_models
            )

        resolved_entries = cls._resolve_provisioning_request(
            request.db, request.provisioning
        )
        cls._verify_matching_tool_version_and_model(
            request.db, request.tool_version, resolved_entries
        )
        cls._verify_model_permissions(
            request.db, request.user, resolved_entries
        )

        if request.session_type == sessions_models.SessionType.PERSISTENT:
            if len(request.provisioning) > 1:
                raise sessions_exceptions.TooManyModelsRequestedToProvisionError(
                    1
                )

            if len(request.provisioning) == 0:
                return interface.ConfigurationHookResult()

            resolved_entry = resolved_entries[0]

            if not provisioning_crud.get_project_provisioning(
                request.db, resolved_entry["model"], request.user
            ):
                await cls._create_provisioning_record(
                    request.db,
                    resolved_entry,
                    request.user,
                )

            environment["WORKSPACE_DIR"] = (
                pathlib.PurePosixPath("/workspace")
                / resolved_entry["project"].slug
                / resolved_entry["model"].slug
            )

        git_repos_with_credentials = cls._get_git_repos_json(
            resolved_entries,
            request.session_type,
            include_credentials=True,
        )

        git_repos_without_credentials = cls._get_git_repos_json(
            resolved_entries,
            request.session_type,
            include_credentials=False,
        )

        init_environment = {
            "CAPELLACOLLAB_PROVISIONING": git_repos_with_credentials
        }

        environment = {
            "CAPELLACOLLAB_SESSION_PROVISIONING": git_repos_without_credentials
        }

        return interface.ConfigurationHookResult(
            init_environment=init_environment, environment=environment
        )

    @classmethod
    def _resolve_provisioning_request(
        cls,
        db: orm.Session,
        entries: list[sessions_models.SessionProvisioningRequest],
    ) -> list[ResolvedSessionProvisioning]:
        """Resolve the model_slugs and git_model_ids from the provisioning request"""
        resolved_entries: list[ResolvedSessionProvisioning] = []
        for entry in entries:
            project = projects_injectables.get_existing_project(
                entry.project_slug, db
            )
            model = toolmodels_injectables.get_existing_capella_model(
                entry.toolmodel_slug, project, db
            )
            resolved_entries.append(
                {
                    "entry": entry,
                    "model": model,
                    "project": project,
                    "git_model": git_injectables.get_existing_git_model(
                        entry.git_model_id, capella_model=model, db=db
                    ),
                }
            )
        return resolved_entries

    @classmethod
    def _verify_matching_tool_version_and_model(
        cls,
        db: orm.Session,
        version: tools_models.DatabaseVersion,
        resolved_entries: list[ResolvedSessionProvisioning],
    ):
        allowed_versions = [
            version
        ] + tools_crud.get_compatible_versions_for_tool_versions(
            db, tool_version=version
        )
        for entry in resolved_entries:
            if entry["model"].version not in allowed_versions:
                raise sessions_exceptions.ToolAndModelMismatchError(
                    tool_name=version.tool.name,
                    version_name=version.name,
                    model_name=entry["model"].name,
                )

    @classmethod
    def _verify_model_permissions(
        cls,
        db: orm.Session,
        user: users_models.DatabaseUser,
        resolved_entries: list[ResolvedSessionProvisioning],
    ):
        """Verify the user has the required permissions for the requested models"""

        for entry in resolved_entries:
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.USER,
                required_permission=projects_users_models.ProjectUserPermission.READ,
            )(project_slug=entry["project"].slug, username=user.name, db=db)

    @classmethod
    def _get_git_repos_json(
        cls,
        resolved_entries: list[ResolvedSessionProvisioning],
        session_type: sessions_models.SessionType,
        include_credentials: bool = False,
    ):
        """Get the git repos as a JSON-serializable list"""
        return [
            cls._git_model_as_json(
                entry["git_model"],
                entry["entry"].revision or entry["git_model"].revision,
                entry["entry"].deep_clone,
                session_type,
                include_credentials,
            )
            for entry in resolved_entries
        ]

    @classmethod
    def _git_model_as_json(
        cls,
        git_model: git_models.DatabaseGitModel,
        revision: str,
        deep_clone: bool,
        session_type: sessions_models.SessionType,
        include_credentials: bool,
    ) -> dict[str, str | int]:
        """Convert a DatabaseGitModel to a JSON-serializable dictionary."""
        toolmodel = git_model.model

        git_dict: dict[str, str | int] = {
            "url": git_model.path,
            "revision": revision,
            "depth": 0 if deep_clone else 1,
            "entrypoint": git_model.entrypoint,
            "nature": (
                git_model.model.nature.name if git_model.model.nature else ""
            ),
            "path": str(
                pathlib.PurePosixPath(
                    toolmodel.tool.config.provisioning.directory
                    if session_type == sessions_models.SessionType.READONLY
                    else "/workspace"
                )
                / toolmodel.project.slug
                / toolmodel.slug
            ),
        }
        if include_credentials and git_model.username:
            git_dict["username"] = git_model.username
            git_dict["password"] = git_model.password
        return git_dict

    @classmethod
    async def _determine_commit_hash(
        cls, revision: str | None, git_model: git_models.DatabaseGitModel
    ) -> tuple[str, str]:
        revision = revision or git_model.revision
        for hash, rev in await instances_git_core.ls_remote(
            url=git_model.path,
            username=git_model.username,
            password=git_model.password,
        ):
            rev = rev.removeprefix("refs/heads/").removeprefix("refs/tags/")
            if rev == revision:
                return revision, hash

        raise instances_git_exceptions.RevisionNotFoundError(revision)

    @classmethod
    async def _create_provisioning_record(
        cls,
        db: orm.Session,
        resolved_entry: ResolvedSessionProvisioning,
        user: users_models.DatabaseUser,
    ) -> None:
        rev, hash = await cls._determine_commit_hash(
            resolved_entry["entry"].revision, resolved_entry["git_model"]
        )
        provisioning_crud.create_project_provisioning(
            db,
            provisioning_models.DatabaseModelProvisioning(
                user=user,
                tool_model=resolved_entry["model"],
                revision=rev,
                commit_hash=hash,
            ),
        )
