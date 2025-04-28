/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { PipelineRun, PipelineRunStatus } from 'src/app/openapi';
import {
  PageWrapperPipelineRun,
  PipelineRunWrapperService,
} from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { mockUser } from 'src/storybook/user';
import { JobRunOverviewComponent } from './job-run-overview.component';

const meta: Meta<JobRunOverviewComponent> = {
  title: 'Pipeline Components/Job Run Overview',
  component: JobRunOverviewComponent,
};

export default meta;
type Story = StoryObj<JobRunOverviewComponent>;

class MockPipelineRunWrapperService
  implements Partial<PipelineRunWrapperService>
{
  private _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(
    undefined,
  );
  public readonly pipelineRun$ = this._pipelineRun.asObservable();

  private _pipelineRunPages = new BehaviorSubject<PageWrapperPipelineRun>({
    pages: [],
    total: undefined,
  });
  public readonly pipelineRunPages$ = this._pipelineRunPages.asObservable();

  constructor(pipelineRunPages: PageWrapperPipelineRun) {
    this._pipelineRunPages.next(pipelineRunPages);
  }
}

export const NoRuns: Story = {
  args: {},
};

export const WithRuns: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineRunWrapperService,
          useValue: new MockPipelineRunWrapperService({
            pages: [
              {
                items: [
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
                ],
                total: null,
                page: null,
                size: null,
                pages: null,
              },
              'loading',
            ],
            total: undefined,
          }),
        },
      ],
    }),
  ],
};
