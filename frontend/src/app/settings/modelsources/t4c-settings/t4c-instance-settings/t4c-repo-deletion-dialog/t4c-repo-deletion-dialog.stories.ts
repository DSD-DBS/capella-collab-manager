/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { userEvent, within } from 'storybook/test';
import { mockSimpleToolModel } from '../../../../../../storybook/model';
import {
  mockT4CInstance,
  mockT4CRepositoryWrapperServiceProvider,
} from '../../../../../../storybook/t4c';
import { T4CRepoDeletionDialogComponent } from './t4c-repo-deletion-dialog.component';

const meta: Meta<T4CRepoDeletionDialogComponent> = {
  title: 'Settings Components/Modelsources/T4C/Delete Repo Dialog',
  component: T4CRepoDeletionDialogComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CRepositoryWrapperServiceProvider([
          {
            id: 1,
            name: 'test-repo',
            instance: mockT4CInstance,
            status: 'ONLINE',
            integrations: [
              {
                id: 1,
                name: 'mockModel',
                model: mockSimpleToolModel,
              },
              {
                id: 2,
                name: 'mockModel 2',
                model: mockSimpleToolModel,
              },
            ],
          },
        ]),
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            id: 1,
            name: 'test-repo',
            instance: mockT4CInstance,
            integrations: [
              {
                id: 1,
                name: 'mockModel',
                model: mockSimpleToolModel,
              },
              {
                id: 2,
                name: 'mockModel 2',
                model: mockSimpleToolModel,
              },
            ],
          },
        },
      ],
    }),
    dialogWrapper,
  ],
};

export default meta;
type Story = StoryObj<T4CRepoDeletionDialogComponent>;

export const Empty: Story = {
  args: {},
};

export const InvalidContent: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const deleteRepoInput = canvas.getByTestId('delete-repo-input');
    await userEvent.type(deleteRepoInput, 'invalid-text');
  },
};

export const ValidContent: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const deleteRepoInput = canvas.getByTestId('delete-repo-input');
    await userEvent.type(deleteRepoInput, 'test-repo');
  },
};
