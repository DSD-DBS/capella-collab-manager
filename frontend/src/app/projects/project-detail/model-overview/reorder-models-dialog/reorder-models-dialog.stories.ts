/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockModel } from 'src/storybook/model';
import { ReorderModelsDialogComponent } from './reorder-models-dialog.component';

const meta: Meta<ReorderModelsDialogComponent> = {
  title: 'Model Components/Reorder Models',
  component: ReorderModelsDialogComponent,
};

export default meta;
type Story = StoryObj<ReorderModelsDialogComponent>;

export const General: Story = {
  args: {},
  decorators: [
    dialogWrapper,
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            projectSlug: 'project-slug',
            models: [mockModel, { ...mockModel, name: 'Coffee Machine' }],
          },
        },
      ],
    }),
  ],
};
