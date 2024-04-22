/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, StoryObj } from '@storybook/angular';
import {
  ConnectionMethod,
  Tool,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { CreateSessionHistoryComponent } from './create-session-history.component';

const meta: Meta<CreateSessionHistoryComponent> = {
  title: 'Session Component / Session History',
  component: CreateSessionHistoryComponent,
};

export default meta;
type Story = StoryObj<CreateSessionHistoryComponent>;

const tool: Tool = {
  id: 1,
  name: 'Tool 1',
  integrations: { t4c: true, pure_variants: true, jupyter: false },
  config: {
    connection: { methods: [] },
    provisioning: {},
    persistent_workspaces: {
      mounting_enabled: true,
    },
  },
};

const version: ToolVersion = {
  id: 1,
  name: 'Version 1',
  config: {
    is_recommended: false,
    is_deprecated: false,
    compatible_versions: [],
  },
};

const connectionMethod: ConnectionMethod = {
  id: '1',
  name: 'Method 1',
  type: 'http',
};

export const ResolvedSessionHistory: Story = {
  args: {
    resolvedHistory: [
      {
        tool: tool,
        version: version,
        lastTimeRequested: new Date(),
        loading: true,
        connectionMethod: connectionMethod,
      },
      {
        tool: { ...tool, name: 'Example tool' },
        version: { ...version, name: 'Example version' },
        lastTimeRequested: new Date('2024-01-01'),
        loading: false,
        connectionMethod: {
          ...connectionMethod,
          name: 'Example connection method',
        },
      },
    ],
    sessionsLoaded: 2,
    sessionsToBeLoaded: 2,
  },
};
