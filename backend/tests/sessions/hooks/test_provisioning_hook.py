# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.sessions import exceptions as sessions_exceptions
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import provisioning as hooks_provisioning
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("project_user")
def test_git_models_are_resolved_correctly(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Make sure that the Git models are correctly translated to environment"""
    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="test",
            deep_clone=False,
        )
    ]

    response = hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
        configuration_hook_request
    )

    expected_response_dict = {
        "url": "https://example.com/test/project",
        "revision": "test",
        "depth": 1,
        "entrypoint": "test/test.aird",
        "nature": "",
        "path": f"/models/{capella_model.project.slug}/{capella_model.slug}",
    }

    assert response["init_environment"]["CAPELLACOLLAB_PROVISIONING"] == [
        expected_response_dict
        | {
            "username": "user",
            "password": "password",
        }
    ]

    assert response["environment"]["CAPELLACOLLAB_SESSION_PROVISIONING"] == [
        expected_response_dict
    ]


async def test_provisioning_fails_missing_permission(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Make sure that provisioning fails when the user does not have the correct permissions"""
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]
    with pytest.raises(fastapi.HTTPException):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            configuration_hook_request
        )


@pytest.mark.usefixtures("project_user")
def test_provisioning_fails_too_many_models_requested(
    capella_tool: tools_models.DatabaseTool,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    capella_tool.config.provisioning.max_number_of_models = 1

    session_provisioning_request = sessions_models.SessionProvisioningRequest(
        project_slug=project.slug,
        model_slug=capella_model.slug,
        git_model_id=git_model.id,
        revision="main",
        deep_clone=False,
    )

    configuration_hook_request.provisioning = [
        session_provisioning_request,
        session_provisioning_request,
    ]
    with pytest.raises(
        sessions_exceptions.TooManyModelsRequestedToProvisionError
    ):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            configuration_hook_request
        )


def test_tool_model_mismatch(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    tool_version: tools_models.DatabaseVersion,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Make sure that provisioning fails when the provided model doesn't match the selected tool"""
    configuration_hook_request.tool_version = tool_version
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]
    with pytest.raises(sessions_exceptions.ToolAndModelMismatchError):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            configuration_hook_request
        )


def test_provision_session_with_compatible_tool_versions(
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
    capella_tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Make sure that provisioning is successful when the tool is compatible with the tool of the model"""

    tool_version.config.compatible_versions = [capella_tool_version.id]
    orm.attributes.flag_modified(tool_version, "config")
    db.commit()

    configuration_hook_request.session_type = (
        sessions_models.SessionType.READONLY
    )

    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]
    configuration_hook_request.user.role = users_models.Role.ADMIN
    response = hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
        configuration_hook_request
    )
    assert response["environment"]["CAPELLACOLLAB_SESSION_PROVISIONING"]
