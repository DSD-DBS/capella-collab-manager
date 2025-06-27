/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { PipelineRunStatus } from 'src/app/openapi';
import { mockPipelineRunWrapperServiceProvider } from 'src/storybook/pipeline';
import { mockUser } from 'src/storybook/user';
import { ViewLogsComponent } from './view-logs.component';

const meta: Meta<ViewLogsComponent> = {
  title: 'Pipeline Components/View Logs',
  component: ViewLogsComponent,
};

export default meta;
type Story = StoryObj<ViewLogsComponent>;

export const Default: Story = {
  args: {
    events: [],
    logs: [],
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockPipelineRunWrapperServiceProvider({
          id: 0,
          reference_id: null,
          triggerer: mockUser,
          trigger_time: '2023-10-01T00:00:00Z',
          status: PipelineRunStatus.Success,
          environment: {},
        }),
      ],
    }),
  ],
};
