/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from '../../../../storybook/model';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from '../../../../storybook/project';
import { InitModelComponent } from './init-model.component';

const meta: Meta<InitModelComponent> = {
  title: 'Model Components/Init Model',
  component: InitModelComponent,
};

export default meta;
type Story = StoryObj<InitModelComponent>;

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, []),
        mockProjectWrapperServiceProvider(undefined, [
          {
            ...mockProject,
            name: 'Internal project',
            visibility: 'internal',
          },
        ]),
      ],
    }),
  ],
};
