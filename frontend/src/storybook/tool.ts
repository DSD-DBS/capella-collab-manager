/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject, filter, Observable } from 'rxjs';
import {
  HTTPConnectionMethodOutput,
  Tool,
  ToolNature,
  ToolSessionConfigurationOutput,
  ToolVersion,
  ToolVersionConfigurationOutput,
  ToolVersionWithTool,
} from 'src/app/openapi';
import { ToolWrapperService } from 'src/app/settings/core/tools-settings/tool.service';

export const mockHttpConnectionMethod: Readonly<HTTPConnectionMethodOutput> = {
  id: '1',
  name: 'HTTP Connection',
  description: 'Connect directly to the session via the browser.',
  type: 'http',
  ports: {
    http: 0,
    metrics: 0,
    additional: {},
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

export const defaultToolConfig: ToolSessionConfigurationOutput = {
  connection: {
    methods: [mockHttpConnectionMethod],
  },
  provisioning: {
    directory: '/tmp',
    max_number_of_models: null,
    required: false,
    provide_diagram_cache: false,
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
  },
  config: defaultToolConfig,
};

export const mockTrainingControllerTool: Readonly<Tool> = {
  id: 2,
  name: 'Training Controller',
  integrations: {
    t4c: false,
    pure_variants: false,
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

class MockToolWrapperService implements Partial<ToolWrapperService> {
  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }
  get tools$(): Observable<Tool[] | undefined> {
    return this._tools.asObservable();
  }

  constructor(tools: Tool[] | undefined = undefined) {
    this._tools.next(tools);
  }

  getTools(): Observable<Tool[]> {
    return this._tools.asObservable().pipe(filter(Boolean));
  }
}

export const mockToolWrapperServiceProvider = (
  tools: Tool[] | undefined = undefined,
) => {
  return {
    provide: ToolWrapperService,
    useValue: new MockToolWrapperService(tools),
  };
};
