/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  HTTPConnectionMethodOutput,
  Tool,
  ToolNature,
  ToolSessionConfigurationOutput,
  ToolVersion,
  ToolVersionConfigurationOutput,
} from 'src/app/openapi';
import { ToolVersionWithTool } from 'src/app/settings/core/tools-settings/tool.service';

export const mockHttpConnectionMethod: Readonly<HTTPConnectionMethodOutput> = {
  id: '1',
  name: 'HTTP Connection',
  description: 'Connect directly to the session via the browser.',
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

const defaultToolVersionConfig: ToolVersionConfigurationOutput = {
  is_recommended: false,
  is_deprecated: false,
  compatible_versions: [],
  sessions: {
    persistent: {
      image: {
        regular: 'docker.io/hello-world:latest',
        beta: null,
      },
    },
  },
  backups: {
    image: 'docker.io/hello-world:latest',
  },
};

export const mockCapellaToolVersion: Readonly<ToolVersion> = {
  id: 1,
  name: '7.0.0',
  config: defaultToolVersionConfig,
};

export const mockOtherToolVersion: Readonly<ToolVersion> = {
  id: 2,
  name: 'Latest',
  config: defaultToolVersionConfig,
};

export const mockToolNature: Readonly<ToolNature> = {
  id: 1,
  name: 'Project',
};

const defaultToolConfig: ToolSessionConfigurationOutput = {
  connection: {
    methods: [mockHttpConnectionMethod],
  },
  provisioning: {
    directory: '/tmp',
    max_number_of_models: null,
    required: false,
  },
  persistent_workspaces: {
    mounting_enabled: true,
  },
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
    logging: {
      enabled: true,
      path: '/workspace/*.log',
    },
  },
  supported_project_types: ['general', 'training'],
};

export const mockCapellaTool: Readonly<Tool> = {
  id: 1,
  name: 'Eclipse Capella',
  integrations: {
    t4c: true,
    pure_variants: true,
    jupyter: false,
  },
  config: defaultToolConfig,
};

export const mockTrainingControllerTool: Readonly<Tool> = {
  id: 2,
  name: 'Training Controller',
  integrations: {
    t4c: false,
    pure_variants: false,
    jupyter: false,
  },
  config: { ...defaultToolConfig, supported_project_types: ['training'] },
};

export const mockToolVersionWithTool: Readonly<ToolVersionWithTool> = {
  ...mockCapellaToolVersion,
  tool: mockCapellaTool,
};

export const mockTrainingControllerVersionWithTool: Readonly<ToolVersionWithTool> =
  {
    ...mockOtherToolVersion,
    tool: mockTrainingControllerTool,
  };
