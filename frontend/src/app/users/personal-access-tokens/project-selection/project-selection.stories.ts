/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { dialogWrapper } from 'src/storybook/decorators';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { ProjectSelectionComponent } from './project-selection.component';

const meta: Meta<ProjectSelectionComponent> = {
  title: 'Settings Components/Personal Access Tokens/Project Selection',
  component: ProjectSelectionComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<ProjectSelectionComponent>;

export const ProjectSelection: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(undefined, [mockProject]),
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            excludeProjects: [],
          },
        },
      ],
    }),
  ],
};
