/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import {
  Pipeline,
  PipelineService,
} from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { TriggerPipelineComponent } from 'src/app/projects/models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { UserService } from 'src/app/services/user/user.service';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockPrimaryGitModel } from 'src/storybook/git';
import { mockTeamForCapellaRepository } from 'src/storybook/t4c';
import { MockUserService } from 'src/storybook/user';

const meta: Meta<TriggerPipelineComponent> = {
  title: 'Pipeline Components / Trigger Pipeline',
  component: TriggerPipelineComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { projectSlug: 'test', modelSlug: 'test' },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<TriggerPipelineComponent>;

class MockPipelineService implements Partial<PipelineService> {
  public readonly pipelines$: Observable<Pipeline[] | undefined> =
    of(undefined);

  constructor(pipelines?: Pipeline[] | undefined) {
    this.pipelines$ = of(pipelines);
  }
}

export const NoPipelineFound: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineService,
          useFactory: () => new MockPipelineService([]),
        },
      ],
    }),
  ],
};

export const LoadingPipelines: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineService,
          useFactory: () => new MockPipelineService(undefined),
        },
      ],
    }),
  ],
};

const pipeline = {
  id: 1,
  t4c_model: mockTeamForCapellaRepository,
  git_model: mockPrimaryGitModel,
  run_nightly: false,
  include_commit_history: false,
};

export const PipelineOverview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineService,
          useFactory: () =>
            new MockPipelineService([
              pipeline,
              {
                ...pipeline,
                id: 2,
                run_nightly: true,
                include_commit_history: true,
              },
            ]),
        },
      ],
    }),
  ],
};

export const OnePipelineSelected: Story = {
  args: { selectedPipeline: pipeline },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineService,
          useFactory: () => new MockPipelineService([pipeline]),
        },
      ],
    }),
  ],
};

export const ForcePipelineDeletion: Story = {
  args: { selectedPipeline: pipeline },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineService,
          useFactory: () => new MockPipelineService([pipeline]),
        },
        {
          provide: UserService,
          useFactory: () => new MockUserService('administrator'),
        },
      ],
    }),
  ],
};
