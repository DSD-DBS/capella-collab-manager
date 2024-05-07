/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  ConnectionMethod,
  Tool,
  ToolVersion,
  ToolVersionWithTool,
} from 'src/app/settings/core/tools-settings/tool.service';

export const mockHttpConnectionMethod: Readonly<ConnectionMethod> = {
  id: '1',
  name: 'fakeConnectionMethod',
  description: 'fakeConnectionMethodDescription',
  type: 'http',
};

export const mockToolVersion: Readonly<ToolVersion> = {
  id: 1,
  name: 'fakeVersion',
  config: {
    is_recommended: false,
    is_deprecated: false,
    compatible_versions: [],
  },
};

export const mockTool: Readonly<Tool> = {
  id: 1,
  name: 'fakeTool',
  integrations: {
    t4c: true,
    pure_variants: true,
    jupyter: false,
  },
  config: {
    connection: {
      methods: [mockHttpConnectionMethod],
    },
    provisioning: {},
    persistent_workspaces: { mounting_enabled: true },
  },
};

export const mockToolVersionWithTool: Readonly<ToolVersionWithTool> = {
  ...mockToolVersion,
  tool: mockTool,
};
