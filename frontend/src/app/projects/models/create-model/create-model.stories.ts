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
import {
  mockCapellaTool,
  mockToolWrapperServiceProvider,
  mockTrainingControllerTool,
} from 'src/storybook/tool';
import { CreateModelComponent } from './create-model.component';

const meta: Meta<CreateModelComponent> = {
  title: 'Model Components/Create Model',
  component: CreateModelComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, undefined),
        mockModelWrapperServiceProvider(mockModel, undefined),
        mockToolWrapperServiceProvider([
          mockCapellaTool,
          mockTrainingControllerTool,
        ]),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<CreateModelComponent>;

export const General: Story = {
  args: {},
};
