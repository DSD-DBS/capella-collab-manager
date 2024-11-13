/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import {
  mockHttpConnectionMethod,
  mockCapellaTool,
  mockCapellaToolVersion,
} from 'src/storybook/tool';
import { CreateSessionHistoryComponent } from './create-session-history.component';

const meta: Meta<CreateSessionHistoryComponent> = {
  title: 'Session Components/Session History',
  component: CreateSessionHistoryComponent,
  parameters: {
    screenshot: {
      viewport: {
        width: 426,
        height: 330,
      },
      viewports: [],
    },
  },
};

export default meta;
type Story = StoryObj<CreateSessionHistoryComponent>;

export const ResolvedSessionHistory: Story = {
  args: {
    resolvedHistory: [
      {
        tool: mockCapellaTool,
        version: mockCapellaToolVersion,
        lastTimeRequested: new Date('2024-04-01'),
        loading: true,
        connectionMethod: {
          ...mockHttpConnectionMethod,
          type: 'http',
          environment: {},
        },
      },
      {
        tool: { ...mockCapellaTool, name: 'Example tool' },
        version: { ...mockCapellaToolVersion, name: 'Example version' },
        lastTimeRequested: new Date('2024-01-01'),
        loading: false,
        connectionMethod: {
          ...mockHttpConnectionMethod,
          name: 'Example connection method',
          type: 'http',
          environment: {},
        },
      },
    ],
    sessionsLoaded: 2,
    sessionsToBeLoaded: 2,
  },
};
