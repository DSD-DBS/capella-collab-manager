# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.tools import models as tools_models

from . import (
    guacamole,
    http,
    interface,
    log_collector,
    networking,
    persistent_workspace,
    project_scope,
    project_volume,
    provisioning,
    pure_variants,
    read_only_workspace,
    session_preparation,
    session_token,
    t4c,
)

REGISTERED_HOOKS: dict[str, interface.HookRegistration] = {
    "t4c": t4c.T4CIntegration(),
    "pure_variants": pure_variants.PureVariantsIntegration(),
}

REGISTER_HOOKS_AUTO_USE: list[interface.HookRegistration] = [
    persistent_workspace.PersistentWorkspaceHook(),
    session_token.SessionTokenIntegration(),
    guacamole.GuacamoleIntegration(),
    http.HTTPIntegration(),
    read_only_workspace.ReadOnlyWorkspaceHook(),
    project_scope.ProjectScopeHook(),
    provisioning.ProvisionWorkspaceHook(),
    session_preparation.GitRepositoryCloningHook(),
    networking.NetworkingIntegration(),
    log_collector.LogCollectorIntegration(),
    project_volume.ProjectVolumeIntegration(),
]


def get_activated_integration_hooks(
    tool: tools_models.DatabaseTool,
) -> list[interface.HookRegistration]:
    """Returns a list of all activated integration hooks for a tool."""
    return [
        hook
        for integration, hook in REGISTERED_HOOKS.items()
        if getattr(tool.integrations, integration, False)
    ] + REGISTER_HOOKS_AUTO_USE
