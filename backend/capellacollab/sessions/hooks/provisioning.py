# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

from sqlalchemy import orm

from capellacollab.core import models as core_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.diagrams import core as diagrams_core
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
from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.settings.modelsources.git import core as instances_git_core
from capellacollab.settings.modelsources.git import (
    exceptions as instances_git_exceptions,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

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
        if len(request.provisioning) == 0:
            if request.tool.config.provisioning.required:
                raise sessions_exceptions.ProvisioningRequiredError()
            return interface.ConfigurationHookResult(
                environment={"CAPELLACOLLAB_SESSION_PROVISIONING": []}
            )

        cls._verify_max_number_of_models(request)

        resolved_entries = cls._resolve_provisioning_request(
            request.db, request.provisioning
        )
        cls._verify_matching_tool_version_and_model(
            request.db, request.tool_version, resolved_entries
        )
        cls._verify_model_permissions(
            request.db,
            resolved_entries,
            request.user,
            request.pat,
            request.global_scope,
        )

        init_environment: dict[str, str] = {}
        environment: dict[str, str] = {}
        warnings: list[core_models.Message] = []
        if request.session_type == sessions_models.SessionType.PERSISTENT:
            await cls._persistent_provisioning(
                request,
                resolved_entries,
                init_environment,
                environment,
                warnings,
            )
        else:
            await cls._read_only_provisioning(
                request, resolved_entries, init_environment, environment
            )

        return interface.ConfigurationHookResult(
            init_environment=init_environment,
            environment=environment,
            warnings=warnings,
        )

    @classmethod
    async def _persistent_provisioning(
        cls,
        request: interface.ConfigurationHookRequest,
        resolved_entries: list[ResolvedSessionProvisioning],
        init_environment: dict[str, t.Any],
        environment: dict[str, t.Any],
        warnings: list[core_models.Message],
    ):
        """Provisioning for persistent sessions"""

        if not request.project_scope:
            raise sessions_exceptions.ProjectScopeRequiredError()

        cls._verify_matching_project_and_model(
            request.project_scope, resolved_entries
        )

        init_provisioning: list[dict[str, str | int]] = []
        session_provisioning: list[dict[str, str | int]] = []

        for resolved_entry in resolved_entries:
            existing_provisioning = provisioning_crud.get_model_provisioning(
                request.db, resolved_entry["model"], request.user
            )

            entry = resolved_entry["entry"]
            git_model = resolved_entry["git_model"]

            if existing_provisioning:
                entry.revision = existing_provisioning.commit_hash
            else:
                provisioning = await cls._create_provisioning_record(
                    request.db,
                    resolved_entry,
                    request.user,
                )

                # Set revision to the actual commit hash
                entry.revision = provisioning.commit_hash

            if not entry.deep_clone:
                warnings.append(
                    core_models.Message(
                        err_code="DEEP_CLONE_REQUIRED",
                        title="Deep clone required.",
                        reason=(
                            "Deep clone is required for persistent provisioning."
                            " The provisioning will continue with deep clone."
                        ),
                    )
                )
                entry.deep_clone = True

            if not existing_provisioning:
                init_provisioning.append(
                    await cls._git_model_as_json(
                        request=request,
                        git_model=git_model,
                        revision=entry.revision or git_model.revision,
                        deep_clone=entry.deep_clone,
                        include_credentials=True,
                    )
                )

            session_provisioning.append(
                await cls._git_model_as_json(
                    request=request,
                    git_model=git_model,
                    revision=entry.revision or git_model.revision,
                    deep_clone=entry.deep_clone,
                    include_credentials=False,
                )
            )

        init_environment["CAPELLACOLLAB_PROVISIONING"] = init_provisioning
        environment["CAPELLACOLLAB_SESSION_PROVISIONING"] = (
            session_provisioning
        )

    @classmethod
    async def _read_only_provisioning(
        cls,
        request: interface.ConfigurationHookRequest,
        resolved_entries: list[ResolvedSessionProvisioning],
        init_environment: dict[str, t.Any],
        environment: dict[str, t.Any],
    ):
        """Provisioning of read-only sessions"""

        init_environment[
            "CAPELLACOLLAB_PROVISIONING"
        ] = await cls._get_git_repos_json(
            request,
            resolved_entries,
            include_credentials=True,
        )

        environment[
            "CAPELLACOLLAB_SESSION_PROVISIONING"
        ] = await cls._get_git_repos_json(
            request,
            resolved_entries,
            include_credentials=False,
            diagram_cache=request.tool.config.provisioning.provide_diagram_cache,
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
    def _verify_max_number_of_models(
        cls, request: interface.ConfigurationHookRequest
    ):
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

    @classmethod
    def _verify_matching_tool_version_and_model(
        cls,
        db: orm.Session,
        version: tools_models.DatabaseVersion,
        resolved_entries: list[ResolvedSessionProvisioning],
    ):
        allowed_versions = [
            version,
            *tools_crud.get_compatible_versions_for_tool_versions(
                db, tool_version=version
            ),
        ]
        for entry in resolved_entries:
            if entry["model"].version not in allowed_versions:
                raise sessions_exceptions.ToolAndModelMismatchError(
                    tool_name=version.tool.name,
                    version_name=version.name,
                    model_name=entry["model"].name,
                )

    @classmethod
    def _verify_matching_project_and_model(
        cls,
        project: projects_models.DatabaseProject,
        resolved_entries: list[ResolvedSessionProvisioning],
    ):
        for entry in resolved_entries:
            if entry["project"] != project:
                raise sessions_exceptions.ProjectAndModelMismatchError(
                    project_slug=project.slug,
                    model_name=entry["model"].name,
                )

    @classmethod
    def _verify_model_permissions(
        cls,
        db: orm.Session,
        resolved_entries: list[ResolvedSessionProvisioning],
        user: users_models.DatabaseUser,
        pat: tokens_models.DatabaseUserToken | None,
        global_scope: permissions_models.GlobalScopes,
    ):
        """Verify the user has the required permissions for the requested models"""

        for entry in resolved_entries:
            project_scope = projects_permissions_injectables.get_scope(
                (user, pat), global_scope, entry["project"], db
            )
            projects_permissions_injectables.ProjectPermissionValidation(
                projects_permissions_models.ProjectUserScopes(
                    provisioning={permissions_models.UserTokenVerb.GET}
                )
            )(project_scope, entry["project"])

    @classmethod
    async def _get_git_repos_json(
        cls,
        request: interface.ConfigurationHookRequest,
        resolved_entries: list[ResolvedSessionProvisioning],
        include_credentials: bool = False,
        diagram_cache: bool = False,
    ) -> list[dict[str, str | int]]:
        """Get the git repos as a JSON-serializable list"""
        return [
            await cls._git_model_as_json(
                request,
                entry["git_model"],
                entry["entry"].revision or entry["git_model"].revision,
                entry["entry"].deep_clone,
                include_credentials,
                diagram_cache,
            )
            for entry in resolved_entries
        ]

    @classmethod
    async def _git_model_as_json(
        cls,
        request: interface.ConfigurationHookRequest,
        git_model: git_models.DatabaseGitModel,
        revision: str,
        deep_clone: bool,
        include_credentials: bool,
        diagram_cache: bool = False,
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
                    if request.session_type
                    == sessions_models.SessionType.READONLY
                    else "/workspace"
                )
                / toolmodel.project.slug
                / toolmodel.slug
            ),
        }

        if include_credentials and git_model.username:
            git_dict["username"] = git_model.username
            git_dict["password"] = git_model.password

        if diagram_cache:
            git_dict[
                "diagram_cache"
            ] = await diagrams_core.build_diagram_cache_api_url(
                request.logger, git_model, request.db, revision
            )

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
            rev_without_prefix = rev.removeprefix("refs/heads/").removeprefix(
                "refs/tags/"
            )
            if rev_without_prefix == revision:
                return revision, hash

        raise instances_git_exceptions.RevisionNotFoundError(revision)

    @classmethod
    async def _create_provisioning_record(
        cls,
        db: orm.Session,
        resolved_entry: ResolvedSessionProvisioning,
        user: users_models.DatabaseUser,
    ) -> provisioning_models.DatabaseModelProvisioning:
        rev, commit_hash = await cls._determine_commit_hash(
            resolved_entry["entry"].revision, resolved_entry["git_model"]
        )
        return provisioning_crud.create_model_provisioning(
            db,
            provisioning_models.DatabaseModelProvisioning(
                user=user,
                tool_model=resolved_entry["model"],
                revision=rev,
                commit_hash=commit_hash,
            ),
        )
