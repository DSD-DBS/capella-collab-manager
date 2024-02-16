# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.tools import models as tools_models

from . import (
    guacamole,
    http,
    interface,
    jupyter,
    persistent_workspace,
    provisioning,
    pure_variants,
    read_only_workspace,
    t4c,
)

REGISTERED_HOOKS: dict[str, interface.HookRegistration] = {
    "jupyter": jupyter.JupyterIntegration(),
    "t4c": t4c.T4CIntegration(),
    "pure_variants": pure_variants.PureVariantsIntegration(),
}

REGISTER_HOOKS_AUTO_USE: dict[str, interface.HookRegistration] = {
    "persistent_workspace": persistent_workspace.PersistentWorkspaceHook(),
    "guacamole": guacamole.GuacamoleIntegration(),
    "http": http.HTTPIntegration(),
    "read_only_hook": read_only_workspace.ReadOnlyWorkspaceHook(),
    "provisioning": provisioning.ProvisionWorkspaceHook(),
}


def get_activated_integration_hooks(
    tool: tools_models.DatabaseTool,
) -> list[interface.HookRegistration]:
    """Returns a list of all activated integration hooks for a tool."""
    return [
        hook
        for integration, hook in REGISTERED_HOOKS.items()
        if getattr(tool.integrations, integration, False)
    ] + list(REGISTER_HOOKS_AUTO_USE.values())
