/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import MockDate from 'mockdate';
import { Observable, of } from 'rxjs';
import { Pipeline } from 'src/app/openapi';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { TriggerPipelineComponent } from 'src/app/projects/models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { mockBackup } from 'src/storybook/backups';
import { dialogWrapper } from 'src/storybook/decorators';

const meta: Meta<TriggerPipelineComponent> = {
  title: 'Pipeline Components/Trigger Pipeline',
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
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<TriggerPipelineComponent>;

class MockPipelineService implements Partial<PipelineWrapperService> {
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
          provide: PipelineWrapperService,
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
          provide: PipelineWrapperService,
          useFactory: () => new MockPipelineService(undefined),
        },
      ],
    }),
  ],
};

export const PipelineOverview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineWrapperService,
          useFactory: () =>
            new MockPipelineService([
              mockBackup,
              {
                ...mockBackup,
                id: 2,
                run_nightly: true,
                next_run: '2024-05-01T03:23:00Z',
              },
            ]),
        },
      ],
    }),
  ],
};

export const PipelineShortly: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: PipelineWrapperService,
          useFactory: () =>
            new MockPipelineService([
              {
                ...mockBackup,
                id: 2,
                run_nightly: true,
                next_run: '2024-04-30T23:59:00Z',
              },
            ]),
        },
      ],
    }),
  ],
};
