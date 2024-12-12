# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pytest
from sqlalchemy import orm

from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
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
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import provisioning as hooks_provisioning
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_read_only_git_models_are_resolved_correctly(
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

    response = await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
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


@pytest.mark.asyncio
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
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_provisioning_fails_too_many_models_requested(
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
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
async def test_tool_model_mismatch(
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
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_read_only_provisioning_session_with_compatible_tool_versions(
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
    response = await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
        configuration_hook_request
    )
    assert response["environment"]["CAPELLACOLLAB_SESSION_PROVISIONING"]


@pytest.mark.asyncio
async def test_request_fails_if_provisioning_is_required(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that a request without provisioning information fails

    If the tool requires provisioning, but no provisioning information
    is provided, the request should fail.
    """

    configuration_hook_request.tool.config.provisioning.required = True

    with pytest.raises(sessions_exceptions.ProvisioningRequiredError):
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_ls_remote", "project_user")
async def test_persistent_provisioning_init(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test the initial provisioning of a persistent provisioning"""

    configuration_hook_request.project_scope = project
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]
    response = await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
        configuration_hook_request
    )

    provisioning = provisioning_crud.get_model_provisioning(
        db, capella_model, user
    )
    assert provisioning is not None
    assert (
        provisioning.commit_hash == "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847"
    )

    init_provisioning = response["init_environment"][
        "CAPELLACOLLAB_PROVISIONING"
    ]
    assert len(init_provisioning) == 1
    assert (
        init_provisioning[0]["revision"]
        == "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847"
    )

    session_provisioning = response["environment"][
        "CAPELLACOLLAB_SESSION_PROVISIONING"
    ]
    assert len(session_provisioning) == 1
    assert "password" not in session_provisioning[0]


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_persistent_provisioning(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    provisioning: provisioning_models.DatabaseModelProvisioning,
):
    """Test skipping the provisioning if already provisioned"""

    configuration_hook_request.project_scope = project
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]
    response = await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
        configuration_hook_request
    )

    assert len(response["init_environment"]["CAPELLACOLLAB_PROVISIONING"]) == 0

    session_provisioning = response["environment"][
        "CAPELLACOLLAB_SESSION_PROVISIONING"
    ]
    assert len(session_provisioning) == 1
    assert "password" not in session_provisioning[0]
    assert session_provisioning[0]["revision"] == provisioning.commit_hash


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_persistent_provisioning_required_project_scope(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that a request without project_scope is declined"""

    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]

    with pytest.raises(sessions_exceptions.ProjectScopeRequiredError):
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("project_user")
async def test_persistent_provisioning_project_mismatch(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """If a provisioning is requested for a another project, fail."""

    project2 = projects_crud.create_project(db, "project2")
    configuration_hook_request.project_scope = project2
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            revision="main",
            deep_clone=False,
        )
    ]

    with pytest.raises(sessions_exceptions.ProjectAndModelMismatchError):
        await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
            configuration_hook_request
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_ls_remote", "project_user")
async def test_provisioning_fallback_without_revision(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
):
    """Test that the provisioning falls back to the default revision
    if no provision is provided"""

    configuration_hook_request.project_scope = project
    configuration_hook_request.provisioning = [
        sessions_models.SessionProvisioningRequest(
            project_slug=project.slug,
            model_slug=capella_model.slug,
            git_model_id=git_model.id,
            deep_clone=False,
        )
    ]

    response = await hooks_provisioning.ProvisionWorkspaceHook().async_configuration_hook(
        configuration_hook_request
    )

    provisioning = provisioning_crud.get_model_provisioning(
        db, capella_model, user
    )
    assert provisioning is not None
    assert provisioning.revision == git_model.revision

    session_provisioning = response["environment"][
        "CAPELLACOLLAB_SESSION_PROVISIONING"
    ]
    assert len(session_provisioning) == 1
    assert (
        session_provisioning[0]["revision"]
        == "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847"
    )
