/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { of } from 'rxjs';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockModel } from 'src/storybook/model';
import { mockProject } from 'src/storybook/project';
import { MoveModelComponent } from './move-model.component';

const meta: Meta<MoveModelComponent> = {
  title: 'Model Components/Move Model',
  component: MoveModelComponent,
};

export default meta;
type Story = StoryObj<MoveModelComponent>;

export const MoveNotAllowed: Story = {
  args: {},
  decorators: [
    dialogWrapper,
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            projectSlug: 'project-slug',
            model: mockModel,
          },
        },
      ],
    }),
  ],
};

export const MoveModel: Story = {
  args: {
    filteredProjects$: of([
      mockProject,
      { ...mockProject, name: 'Coffee Machine' },
    ]),
  },
  decorators: [
    dialogWrapper,
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            projectSlug: 'project-slug',
            model: mockModel,
          },
        },
      ],
    }),
  ],
};
