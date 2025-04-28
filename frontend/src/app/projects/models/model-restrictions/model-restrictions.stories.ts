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
import { mockTrainingControllerTool } from '../../../../storybook/tool';
import { ModelRestrictionsComponent } from './model-restrictions.component';

const meta: Meta<ModelRestrictionsComponent> = {
  title: 'Model Components/Model Restrictions',
  component: ModelRestrictionsComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectWrapperServiceProvider(mockProject, [mockProject]),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<ModelRestrictionsComponent>;

export const AllowPureVariants: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(mockModel, [mockModel])],
    }),
  ],
};

export const Loading: Story = {
  args: {
    loading: true,
  },
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(mockModel, [mockModel])],
    }),
  ],
};

const mockModelNoPureVariants = {
  ...mockModel,
  tool: mockTrainingControllerTool,
};

export const NoRestrictions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModelNoPureVariants, [
          mockModelNoPureVariants,
        ]),
      ],
    }),
  ],
};
