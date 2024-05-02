/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, StoryObj } from '@storybook/angular';
import {
  mockHttpConnectionMethod,
  mockTool,
  mockToolVersion,
} from 'src/storybook/tool';
import { CreateSessionHistoryComponent } from './create-session-history.component';

const meta: Meta<CreateSessionHistoryComponent> = {
  title: 'Session Components / Session History',
  component: CreateSessionHistoryComponent,
};

export default meta;
type Story = StoryObj<CreateSessionHistoryComponent>;

export const ResolvedSessionHistory: Story = {
  args: {
    resolvedHistory: [
      {
        tool: mockTool,
        version: mockToolVersion,
        lastTimeRequested: new Date('2024-04-01'),
        loading: true,
        connectionMethod: {
          ...mockHttpConnectionMethod,
          type: 'http',
          environment: {},
        },
      },
      {
        tool: { ...mockTool, name: 'Example tool' },
        version: { ...mockToolVersion, name: 'Example version' },
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
