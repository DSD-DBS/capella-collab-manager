/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { of } from 'rxjs';
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
import { CreateModelBaseComponent } from './create-model-base.component';

const meta: Meta<CreateModelBaseComponent> = {
  title: 'Model Components/Model Base',
  component: CreateModelBaseComponent,
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
type Story = StoryObj<CreateModelBaseComponent>;

export const General: Story = {
  args: {
    $tools: of([mockCapellaTool, mockTrainingControllerTool]),
  },
};
