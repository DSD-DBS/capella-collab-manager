/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { ModelDescriptionComponent } from './model-description.component';

const meta: Meta<ModelDescriptionComponent> = {
  title: 'Model Components/Model Description',
  component: ModelDescriptionComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, [mockProject]),
        mockModelWrapperServiceProvider(mockModel, [mockModel]),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<ModelDescriptionComponent>;

export const General: Story = {
  args: {},
};
