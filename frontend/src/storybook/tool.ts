/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  HTTPConnectionMethodOutput,
  Tool,
  ToolNature,
  ToolVersion,
} from 'src/app/openapi';
import { ToolVersionWithTool } from 'src/app/settings/core/tools-settings/tool.service';

export const mockHttpConnectionMethod: Readonly<HTTPConnectionMethodOutput> = {
  id: '1',
  name: 'fakeConnectionMethod',
  description: 'fakeConnectionMethodDescription',
  type: 'http',
  ports: {
    http: 0,
    metrics: 0,
  },
  environment: {},
  redirect_url: 'https://example.com',
  cookies: {},
  sharing: {
    enabled: false,
  },
};

export const mockToolVersion: Readonly<ToolVersion> = {
  id: 1,
  name: 'fakeVersion',
  config: {
    is_recommended: false,
    is_deprecated: false,
    compatible_versions: [],
    sessions: {
      persistent: {
        image: 'fakeImage',
      },
    },
    backups: {
      image: 'fakeImage',
    },
  },
};

export const mockToolNature: Readonly<ToolNature> = {
  id: 1,
  name: 'fakeNature',
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
      methods: [{ ...mockHttpConnectionMethod, type: 'http', environment: {} }],
    },
    provisioning: {
      directory: '/tmp',
      max_number_of_models: null,
    },
    persistent_workspaces: { mounting_enabled: true },
    resources: {
      cpu: {
        requests: 0.5,
        limits: 1,
      },
      memory: {
        requests: '1Gi',
        limits: '2Gi',
      },
    },
    environment: {},
    monitoring: {
      prometheus: {
        path: '/metrics',
      },
    },
  },
};

export const mockToolVersionWithTool: Readonly<ToolVersionWithTool> = {
  ...mockToolVersion,
  tool: mockTool,
};
