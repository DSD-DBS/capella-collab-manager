/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { PipelineRunStatus } from 'src/app/openapi';
import { mockPipelineRunWrapperServiceProvider } from 'src/storybook/pipeline';
import { mockUser } from 'src/storybook/user';
import { JobRunOverviewComponent } from './job-run-overview.component';

const meta: Meta<JobRunOverviewComponent> = {
  title: 'Pipeline Components/Job Run Overview',
  component: JobRunOverviewComponent,
};

export default meta;
type Story = StoryObj<JobRunOverviewComponent>;

export const NoRuns: Story = {
  args: {},
};

export const WithRuns: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockPipelineRunWrapperServiceProvider(undefined, [
          {
            id: 0,
            reference_id: null,
            triggerer: mockUser,
            trigger_time: '2023-10-01T00:00:00Z',
            status: PipelineRunStatus.Success,
            environment: {},
          },
          {
            id: 1,
            reference_id: null,
            triggerer: mockUser,
            trigger_time: '2023-10-01T00:00:00Z',
            status: PipelineRunStatus.Failure,
            environment: {
              SPECIAL_ENVIRONMENT_VAR: 'value',
            },
          },
        ]),
      ],
    }),
  ],
};
