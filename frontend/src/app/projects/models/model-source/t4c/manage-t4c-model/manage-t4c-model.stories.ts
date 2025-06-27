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
  mockExtendedT4CRepository,
  mockT4CInstance,
  mockT4CModel,
  mockT4CModelServiceProvider,
  mockT4CRepositoryWrapperServiceProvider,
} from 'src/storybook/t4c';
import { userEvent, within } from 'storybook/test';
import { ManageT4CModelComponent } from './manage-t4c-model.component';

const meta: Meta<ManageT4CModelComponent> = {
  title: 'Model Components/Model Sources/Update T4C Model',
  component: ManageT4CModelComponent,
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
type Story = StoryObj<ManageT4CModelComponent>;

export const Loading: Story = {
  args: {},
};

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CModelServiceProvider(undefined, undefined, [mockT4CInstance]),
        mockT4CRepositoryWrapperServiceProvider([mockExtendedT4CRepository]),
      ],
    }),
  ],
};

export const NoRepository: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByTestId('t4c-instance'));

    const generalDropdownItem = document.querySelector(
      'mat-option[ng-reflect-value="1"]',
    );
    if (!generalDropdownItem) {
      throw new Error('Dropdown item with value "1" not found');
    }
    await userEvent.click(generalDropdownItem);
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CModelServiceProvider(undefined, undefined, [mockT4CInstance]),
        mockT4CRepositoryWrapperServiceProvider([]),
      ],
    }),
  ],
};

export const NoInstances: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockT4CModelServiceProvider(undefined, undefined, [])],
    }),
  ],
};

export const Modify: Story = {
  args: {
    t4cModel: mockT4CModel,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CModelServiceProvider(mockT4CModel, undefined, [mockT4CInstance]),
        mockT4CRepositoryWrapperServiceProvider([mockExtendedT4CRepository]),
      ],
    }),
  ],
};
