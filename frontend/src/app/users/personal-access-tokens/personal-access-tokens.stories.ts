/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import MockDate from 'mockdate';
import { of } from 'rxjs';
import { FineGrainedResourceOutput, UserToken } from 'src/app/openapi';
import {
  PersonalAccessTokensComponent,
  ProjectScopes,
  Scopes,
} from './personal-access-tokens.component';

const meta: Meta<PersonalAccessTokensComponent> = {
  title: 'Settings Components/Personal Access Tokens',
  component: PersonalAccessTokensComponent,
  decorators: [],
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<PersonalAccessTokensComponent>;

const globalPermissionsSchema: Scopes = {
  $defs: {
    AdminScopes: {
      properties: {
        users: {
          description:
            'Manage all users of the application.\nCREATE/UPDATE can be used to change the role of a user / escalate privileges. Use with caution!',
          items: {
            enum: ['GET', 'CREATE', 'UPDATE', 'DELETE'],
          },
          title: 'Users',
        },
        projects: {
          description:
            'Grant permission to all sub-resources of ALL projects. Use with caution! If possible, use project scopes instead.',
          items: {
            enum: ['GET', 'CREATE', 'UPDATE', 'DELETE'],
          },
          title: 'Projects',
        },
        tools: {
          description: "Manage all tools, including it's versions and natures",
          items: {
            enum: ['GET', 'CREATE', 'UPDATE', 'DELETE'],
          },
          title: 'Tools',
        },
        announcements: {
          description: 'Manage all announcements',
          items: {
            enum: ['CREATE', 'DELETE'],
          },
          title: 'Announcements',
        },
        monitoring: {
          description:
            'Allow access to monitoring dashboards, Prometheus and Grafana',
          items: {
            const: 'GET',
          },
          title: 'Monitoring',
        },
        configuration: {
          description: 'See and update the global configuration',
          items: {
            enum: ['GET', 'UPDATE'],
          },
          title: 'Global Configuration',
        },
        t4c_servers: {
          description: 'Manage Team4Capella servers and license servers',
          items: {
            enum: ['GET', 'CREATE', 'UPDATE', 'DELETE'],
          },
          title: 'TeamForCapella Servers',
        },
        t4c_repositories: {
          description: 'Manage Team4Capella repositories',
          items: {
            enum: ['GET', 'CREATE', 'UPDATE', 'DELETE'],
          },
          title: 'TeamForCapella Repositories',
        },
        pv_configuration: {
          description: 'pure::variants license configuration',
          items: {
            enum: ['UPDATE', 'DELETE'],
          },
          title: 'pure::variants Configuration',
        },
        events: {
          description: 'See all events',
          items: {
            const: 'GET',
          },
          title: 'Events',
        },
      },
      title: 'AdminScopes',
    },
    UserScopes: {
      properties: {
        sessions: {
          description: 'Manage sessions of your own user',
          items: {
            enum: ['GET', 'CREATE', 'DELETE'],
          },
          title: 'Sessions',
        },
        projects: {
          description: 'Create new projects',
          items: {
            const: 'CREATE',
          },
          title: 'Projects',
        },
        tokens: {
          description: 'Manage personal access tokens',
          items: {
            enum: ['GET', 'CREATE', 'DELETE'],
          },
          title: 'Personal Access Tokens',
        },
      },
      title: 'UserScopes',
    },
  },
  properties: {
    user: {
      $ref: '#/$defs/UserScopes',
      title: 'User Scopes',
    },
    admin: {
      $ref: '#/$defs/AdminScopes',
      title: 'Administrator Scopes',
    },
  },
};

const projectPermissionSchema: ProjectScopes = {
  properties: {
    root: {
      description:
        'Add capability to delete the project or update the project metadata (visibility & project type & archiving)',
      items: {
        enum: ['UPDATE', 'DELETE'],
      },
      title: 'Project',
    },
    pipelines: {
      description:
        'See pipelines, create new pipelines or delete existing pipelines',
      items: {
        enum: ['GET', 'CREATE', 'DELETE'],
      },
      title: 'Pipelines',
    },
    pipeline_runs: {
      description: 'Allow access to see or trigger pipeline runs',
      items: {
        enum: ['GET', 'CREATE'],
      },
      title: 'Pipeline Runs',
    },
    diagram_cache: {
      description: 'Fetch diagrams via the diagram cache API',
      items: {
        const: 'GET',
      },
      title: 'Diagrams from the cache',
    },
    t4c_model_links: {
      description: 'See links to TeamForCapella repositories',
      items: {
        const: 'GET',
      },
      title: 'Linked TeamForCapella repositories',
    },
    git_model_links: {
      description: 'Manage links to Git repositories',
      items: {
        enum: ['GET', 'UPDATE', 'CREATE', 'DELETE'],
      },
      title: 'Linked Git repositories',
    },
    tool_models: {
      description:
        'Manage tool models (UPDATE = Update description, version, nature and order of tool model)',
      items: {
        enum: ['GET', 'UPDATE', 'CREATE', 'DELETE'],
      },
      title: 'Tool Models',
    },
    used_tools: {
      description: 'Configure used tools in the project',
      items: {
        enum: ['GET', 'CREATE', 'DELETE'],
      },
      title: 'Used Tools',
    },
    project_users: {
      description:
        'Manage project users UPDATE/CREATE can also be used to update roles / escalate own privileges. Use with caution!',
      items: {
        enum: ['GET', 'UPDATE', 'CREATE', 'DELETE'],
      },
      title: 'Project Users',
    },
    access_log: {
      description: 'Access log of project users',
      items: {
        const: 'GET',
      },
      title: 'Project Users Access Log',
    },
    provisioning: {
      description:
        'Access to provisioned and read-only sessions (includes access to the content of linked Git repositories)',
      items: {
        const: 'GET',
      },
      title: 'Provisioning',
    },
    t4c_access: {
      description:
        'Access to TeamForCapella repositories in persistent sessions (Session token will created with GET access)',
      items: {
        const: 'UPDATE',
      },
      title: 'Access to linked TeamForCapella repositories',
    },
    restrictions: {
      description:
        'Manage restrictions on models (Provide access to pure::variants)',
      items: {
        enum: ['GET', 'UPDATE'],
      },
      title: 'Model Restrictions',
    },
  },
  title: 'ProjectUserScopes',
};

export const NoTokensInOverview: Story = {
  args: {
    expandedTokenScopes: {
      user: true,
      admin: true,
    },
    permissionsSchema: globalPermissionsSchema,
  },
};

export const CreateTokenWithProjectScope: Story = {
  args: {
    expandedTokenScopes: {
      user: false,
      admin: false,
    },
    permissionsSchema: globalPermissionsSchema,
    projectPermissionsSchema: projectPermissionSchema,
    projectScopes: ['in-flight-entertainment'],
  },
  parameters: {
    screenshot: {
      captureBeyondViewport: true,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const checkboxes: string[] = [
      'checkbox-admin-announcements-CREATE',
      'checkbox-admin-projects-UPDATE',
      'checkbox-admin-projects-DELETE',
      'checkbox-admin-tools-GET',
      'checkbox-admin-tools-UPDATE',
      'checkbox-admin-tools-CREATE',
      'checkbox-admin-tools-DELETE',
    ];
    for (const checkbox of checkboxes) {
      await userEvent.click(canvas.getByTestId(checkbox));
    }
  },
};

const scope: FineGrainedResourceOutput = {
  user: {
    sessions: ['GET'],
    projects: [],
    tokens: [],
    feedback: [],
  },
  admin: {
    users: ['GET', 'CREATE'],
    projects: [],
    tools: [],
    announcements: [],
    monitoring: [],
    configuration: [],
    git_servers: [],
    t4c_servers: [],
    t4c_repositories: [],
    pv_configuration: [],
    events: [],
    sessions: [],
    workspaces: [],
    personal_access_tokens: [],
    tags: [],
  },
  projects: {},
};

const userToken: UserToken = {
  id: 1,
  user_id: 1,
  expiration_date: '2024-12-18',
  created_at: '2024-04-01T15:00:00Z',
  title: 'Visual Testing PAT',
  description: 'Token used for visual testing',
  source: 'token overview',
  requested_scopes: scope,
  actual_scopes: {
    user: { ...scope.user },
    admin: { ...scope.admin, users: ['GET'] },
    projects: {},
  },
  managed: false,
};

export const TokenOverview: Story = {
  args: {
    expandedTokenScopes: {
      user: true,
      admin: true,
    },
    permissionsSchema: globalPermissionsSchema,
    tokens$: of([
      userToken,
      {
        id: 2,
        user_id: 1,
        expiration_date: '2024-03-11',
        created_at: '2024-01-01T15:00:00Z',
        title: 'Expired token',
        description: 'Example to show an expired token',
        source: 'token overview',
        requested_scopes: scope,
        actual_scopes: scope,
        managed: false,
      },
      {
        id: 3,
        user_id: 1,
        expiration_date: '2024-07-11',
        created_at: '2024-01-01T15:00:00Z',
        title: 'Example without scopes',
        description: '',
        source: 'token overview',
        requested_scopes: {
          user: { ...scope.user, sessions: [] },
          admin: { ...scope.admin, users: [] },
          projects: {},
        },
        actual_scopes: scope,
        managed: false,
      },
      {
        id: 4,
        user_id: 1,
        expiration_date: '2024-07-11',
        created_at: '2024-01-01T15:00:00Z',
        title: 'Example with one scope',
        description: '',
        source: 'token overview',
        requested_scopes: {
          user: { ...scope.user },
          admin: { ...scope.admin, users: [] },
          projects: {},
        },
        actual_scopes: scope,
        managed: false,
      },
      {
        id: 5,
        user_id: 1,
        expiration_date: '2024-07-11',
        created_at: '2024-01-01T15:00:00Z',
        title: 'Managed token',
        description: 'This is an example of a managed token',
        source: 'token overview',
        requested_scopes: {
          user: { ...scope.user },
          admin: { ...scope.admin, users: [] },
          projects: {},
        },
        actual_scopes: scope,
        managed: true,
      },
    ]),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const scopesExpansionPanel1 = canvas.getByTestId('scopes-expansion-1');
    await userEvent.click(scopesExpansionPanel1);
    const scopesExpansionPanel3 = canvas.getByTestId('scopes-expansion-3');
    await userEvent.click(scopesExpansionPanel3);
  },
};

export const GeneratedTokenHidden: Story = {
  args: {
    expandedTokenScopes: {
      user: true,
      admin: true,
    },
    permissionsSchema: globalPermissionsSchema,
    tokens$: of([userToken]),
    generatedToken: 'collabmanager_b0vcJKqGr5KU7flj9IgfJDiblBGLw7cG',
  },
};

export const GeneratedTokenRevealed: Story = {
  args: {
    expandedTokenScopes: {
      user: true,
      admin: true,
    },
    permissionsSchema: globalPermissionsSchema,
    tokens$: of([userToken]),
    generatedToken: 'collabmanager_b0vcJKqGr5KU7flj9IgfJDiblBGLw7cG',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const showValue = canvas.getByTestId('show-value');
    await userEvent.click(showValue);
  },
};
