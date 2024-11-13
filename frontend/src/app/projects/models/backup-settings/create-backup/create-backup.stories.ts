/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import {
  mockGitModelServiceProvider,
  mockPrimaryGitModel,
} from 'src/storybook/git';
import { mockT4CModel, mockT4CModelServiceProvider } from 'src/storybook/t4c';
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
        mockGitModelServiceProvider(mockPrimaryGitModel, []),
        mockT4CModelServiceProvider(mockT4CModel, []),
      ],
    }),
  ],
};

export const WithLinkedModels: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockGitModelServiceProvider(mockPrimaryGitModel, [
          mockPrimaryGitModel,
          { ...mockPrimaryGitModel, id: 2, primary: false, username: '' },
        ]),
        mockT4CModelServiceProvider(mockT4CModel, [mockT4CModel]),
      ],
    }),
  ],
};

export const RequestSent: Story = {
  args: { loading: true },
  decorators: [
    moduleMetadata({
      providers: [
        mockGitModelServiceProvider(mockPrimaryGitModel, [mockPrimaryGitModel]),
        mockT4CModelServiceProvider(mockT4CModel, [mockT4CModel]),
      ],
    }),
  ],
};
