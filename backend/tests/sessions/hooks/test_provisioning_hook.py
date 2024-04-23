# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json

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
from capellacollab.sessions.hooks import provisioning as hooks_provisioning
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("project_user")
def test_git_models_are_resolved_correctly(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    """Make sure that the Git models are correctly translated to GIT_MODELS environment"""

    response = hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
        db=db,
        tool=capella_tool,
        tool_version=capella_tool_version,
        user=user,
        provisioning=[
            sessions_models.SessionProvisioningRequest(
                project_slug=project.slug,
                model_slug=capella_model.slug,
                git_model_id=git_model.id,
                revision="test",
                deep_clone=False,
            )
        ],
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


def test_provisioning_fails_missing_permission(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    """Make sure that provisioning fails when the user does not have the correct permissions"""
    with pytest.raises(fastapi.HTTPException):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            db=db,
            tool=capella_tool,
            tool_version=capella_tool_version,
            user=user,
            provisioning=[
                sessions_models.SessionProvisioningRequest(
                    project_slug=project.slug,
                    model_slug=capella_model.slug,
                    git_model_id=git_model.id,
                    revision="main",
                    deep_clone=False,
                )
            ],
        )


@pytest.mark.usefixtures("project_user")
def test_provisioning_fails_too_many_models_requested(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    capella_tool.config.provisioning.max_number_of_models = 1

    session_provisioning_request = sessions_models.SessionProvisioningRequest(
        project_slug=project.slug,
        model_slug=capella_model.slug,
        git_model_id=git_model.id,
        revision="main",
        deep_clone=False,
    )

    with pytest.raises(
        sessions_exceptions.TooManyModelsRequestedToProvisionError
    ):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            db=db,
            tool=capella_tool,
            tool_version=capella_tool_version,
            user=user,
            provisioning=[
                session_provisioning_request,
                session_provisioning_request,
            ],
        )


def test_tool_model_mismatch(
    db: orm.Session,
    user: users_models.DatabaseUser,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    """Make sure that provisioning fails when the provided model doesn't match the selected tool"""
    with pytest.raises(sessions_exceptions.ToolAndModelMismatchError):
        hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
            db=db,
            tool=tool,
            tool_version=tool_version,
            user=user,
            provisioning=[
                sessions_models.SessionProvisioningRequest(
                    project_slug=project.slug,
                    model_slug=capella_model.slug,
                    git_model_id=git_model.id,
                    revision="main",
                    deep_clone=False,
                )
            ],
        )


def test_provision_session_with_compatible_tool_versions(
    db: orm.Session,
    admin: users_models.DatabaseUser,
    tool_version: tools_models.DatabaseVersion,
    tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    """Make sure that provisioning is successful when the tool is compatible with the tool of the model"""

    tool_version.config.compatible_versions = [capella_tool_version.id]
    orm.attributes.flag_modified(tool_version, "config")
    db.commit()

    response = hooks_provisioning.ProvisionWorkspaceHook().configuration_hook(
        db=db,
        tool=tool,
        tool_version=tool_version,
        user=admin,
        provisioning=[
            sessions_models.SessionProvisioningRequest(
                project_slug=project.slug,
                model_slug=capella_model.slug,
                git_model_id=git_model.id,
                revision="main",
                deep_clone=False,
            )
        ],
    )
    assert response["environment"]["CAPELLACOLLAB_SESSION_PROVISIONING"]
