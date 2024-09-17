/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { dialogWrapper } from 'src/storybook/decorators';
import { MockGitModelService, mockPrimaryGitModel } from 'src/storybook/git';
import { mockT4CModel, MockT4CModelService } from 'src/storybook/t4c';
import { CreateBackupComponent } from './create-backup.component';

const meta: Meta<CreateBackupComponent> = {
  title: 'Pipeline Components/Create Backup',
  component: CreateBackupComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            projectSlug: 'test',
            modelSlug: 'test',
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<CreateBackupComponent>;

export const Loading: Story = {
  args: {},
};

export const WithoutLinkedModels: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitModelService,
          useFactory: () => new MockGitModelService(mockPrimaryGitModel, []),
        },
        {
          provide: T4CModelService,
          useFactory: () => new MockT4CModelService(mockT4CModel, []),
        },
      ],
    }),
  ],
};

export const WithLinkedModels: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitModelService,
          useFactory: () =>
            new MockGitModelService(mockPrimaryGitModel, [
              mockPrimaryGitModel,
              { ...mockPrimaryGitModel, id: 2, primary: false, username: '' },
            ]),
        },
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(mockT4CModel, [mockT4CModel]),
        },
      ],
    }),
  ],
};

export const RequestSent: Story = {
  args: { loading: true },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitModelService,
          useFactory: () =>
            new MockGitModelService(mockPrimaryGitModel, [mockPrimaryGitModel]),
        },
        {
          provide: T4CModelService,
          useFactory: () =>
            new MockT4CModelService(mockT4CModel, [mockT4CModel]),
        },
      ],
    }),
  ],
};
