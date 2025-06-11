/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { PipelineRunStatus } from 'src/app/openapi';
import { mockPipelineRunWrapperServiceProvider } from 'src/storybook/pipeline';
import { mockUser } from 'src/storybook/user';
import { ViewLogsComponent } from './view-logs.component';

const meta: Meta<ViewLogsComponent> = {
  title: 'Pipeline Components/View Logs',
  component: ViewLogsComponent,
  beforeEach: () => {
    MockDate.set(new Date('2023-10-01 03:00:00'));
  },
};

export default meta;
type Story = StoryObj<ViewLogsComponent>;

export const Pending: Story = {
  args: {
    events: undefined,
    logs: undefined,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockPipelineRunWrapperServiceProvider({
          id: 0,
          reference_id: null,
          triggerer: mockUser,
          trigger_time: '2023-10-01T00:00:00Z',
          status: PipelineRunStatus.Pending,
          environment: {},
        }),
      ],
    }),
  ],
};

export const TriggeredByScheduler: Story = {
  args: {
    events: [
      {
        timestamp: '2023-10-01T00:00:00Z',
        reason: 'Started',
        message: 'Pipeline run triggered by scheduler',
      },
    ],
    logs: [],
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockPipelineRunWrapperServiceProvider({
          id: 0,
          reference_id: null,
          triggerer: null,
          trigger_time: '2023-10-01T00:00:00Z',
          status: PipelineRunStatus.Running,
          environment: {},
        }),
      ],
    }),
  ],
};

export const NoLogs: Story = {
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
          triggerer: null,
          trigger_time: '2023-10-01T00:00:00Z',
          status: PipelineRunStatus.Success,
          environment: {},
        }),
      ],
    }),
  ],
};

export const FailedWithLogs: Story = {
  args: {
    events: [
      {
        timestamp: '2023-10-01T00:00:10Z',
        reason: 'Started',
        message: 'Pipeline run started',
      },
      {
        timestamp: '2023-10-01T00:02:15Z',
        reason: 'Failed',
        message: 'Pipeline run failed due to connection timeout',
      },
    ],
    logs: [
      {
        timestamp: '2023-10-01T00:00:00Z',
        text: 'INFO: Starting backup process...',
      },
      {
        timestamp: '2023-10-01T00:00:05Z',
        text: 'INFO: Connecting to database...',
      },
      {
        timestamp: '2023-10-01T00:00:08Z',
        text: 'INFO: Database connection established',
      },
      {
        timestamp: '2023-10-01T00:00:10Z',
        text: 'INFO: Beginning data export...',
      },
      {
        timestamp: '2023-10-01T00:00:30Z',
        text: 'INFO: Exported 1000 records...',
      },
      {
        timestamp: '2023-10-01T00:01:00Z',
        text: 'INFO: Exported 2000 records...',
      },
      {
        timestamp: '2023-10-01T00:01:30Z',
        text: 'WARNING: Connection seems slow, retrying...',
      },
      {
        timestamp: '2023-10-01T00:01:45Z',
        text: 'INFO: Exported 2500 records...',
      },
      {
        timestamp: '2023-10-01T00:02:00Z',
        text: 'ERROR: Connection timeout after 120 seconds',
      },
      {
        timestamp: '2023-10-01T00:02:05Z',
        text: 'ERROR: Failed to complete backup operation',
      },
      {
        timestamp: '2023-10-01T00:02:10Z',
        text: 'ERROR: Rolling back partial backup...',
      },
      {
        timestamp: '2023-10-01T00:02:12Z',
        text: 'INFO: Cleanup completed',
      },
      {
        timestamp: '2023-10-01T00:02:15Z',
        text: 'FATAL: Backup process terminated with errors',
      },
    ],
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockPipelineRunWrapperServiceProvider({
          id: 0,
          reference_id: null,
          triggerer: null,
          trigger_time: '2023-10-01T00:00:00Z',
          status: PipelineRunStatus.Failure,
          environment: {},
        }),
      ],
    }),
  ],
};
