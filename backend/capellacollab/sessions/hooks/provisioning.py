# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
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
from capellacollab.projects.users import models as projects_users_models
from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
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
    def configuration_hook(  # type: ignore
        cls,
        db: orm.Session,
        tool_version: tools_models.DatabaseVersion,
        user: users_models.DatabaseUser,
        provisioning: list[sessions_models.SessionProvisioningRequest],
        **kwargs,
    ) -> interface.ConfigurationHookResult:
        resolved_entries = cls._resolve_provisioning_request(db, provisioning)
        cls._verify_matching_tool_version_and_model(
            tool_version, resolved_entries
        )
        cls._verify_model_permissions(db, user, resolved_entries)

        return interface.ConfigurationHookResult(
            environment={
                "GIT_REPOS_JSON": json.dumps(
                    cls._get_git_repos_json(resolved_entries)
                )
            }
        )

    @classmethod
    def _provisioning_request_to_git_model_json(
        cls,
        db: orm.Session,
        user: users_models.DatabaseUser,
        version: tools_models.DatabaseVersion,
        entries: list[sessions_models.SessionProvisioningRequest],
    ) -> dict[str, str]:
        resolved_entries = cls._resolve_provisioning_request(db, entries)
        cls._verify_matching_tool_version_and_model(version, resolved_entries)
        cls._verify_model_permissions(db, user, resolved_entries)
        return {
            "GIT_REPOS_JSON": json.dumps(
                cls._get_git_repos_json(resolved_entries)
            )
        }

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
        version: tools_models.DatabaseVersion,
        resolved_entries: list[ResolvedSessionProvisioning],
    ):
        for entry in resolved_entries:
            if entry["model"].version != version:
                raise sessions_exceptions.ToolAndModelMismatchError(
                    version=version, model=entry["model"]
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
    ):
        """Get the git repos as a JSON-serializable list"""
        return [
            cls._git_model_as_json(
                entry["git_model"],
                entry["entry"].revision,
                entry["entry"].deep_clone,
            )
            for entry in resolved_entries
        ]

    @classmethod
    def _git_model_as_json(
        cls,
        git_model: git_models.DatabaseGitModel,
        revision: str,
        deep_clone: bool,
    ) -> dict[str, str | int]:
        """Convert a DatabaseGitModel to a JSON-serializable dictionary."""

        git_dict: dict[str, str | int] = {
            "url": git_model.path,
            "revision": revision,
            "depth": 0 if deep_clone else 1,
            "entrypoint": git_model.entrypoint,
            "nature": (
                git_model.model.nature.name if git_model.model.nature else ""
            ),
        }
        if git_model.username:
            git_dict["username"] = git_model.username
            git_dict["password"] = git_model.password
        return git_dict
