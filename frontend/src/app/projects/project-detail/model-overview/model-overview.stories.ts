/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import {
  mockUser,
  mockOwnUserWrapperServiceProvider,
} from 'src/storybook/user';
import { userEvent, within } from 'storybook/test';
import { ModelOverviewComponent } from './model-overview.component';

const meta: Meta<ModelOverviewComponent> = {
  title: 'Model Components/Model Overview',
  component: ModelOverviewComponent,
};

export default meta;
type Story = StoryObj<ModelOverviewComponent>;

export const Loading: Story = {
  args: {},
};

const models = [
  { ...mockModel, name: 'mockModel1' },
  {
    ...mockModel,
    id: 2,
    name: 'mockModel2',
    description:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  },
  {
    ...mockModel,
    id: 3,
    name: 'ModelWithMissingInfo',
    version: null,
    nature: null,
  },
  {
    ...mockModel,
    id: 4,
    name: 'Capella model',
    tool: { ...mockModel.tool, name: 'Capella' },
  },
];

export const AsProjectUserRead: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(mockModel, models)],
    }),
  ],
};

export const AsProjectUserWrite: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, models),
        mockProjectUserServiceProvider('user', 'write'),
      ],
    }),
  ],
};

export const AsProjectAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, models),
        mockProjectUserServiceProvider('manager', 'write'),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByTestId('more-options-1'));
  },
};

export const AsGlobalAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, models),
        mockProjectUserServiceProvider('manager', 'write'),
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByTestId('more-options-1'));
  },
};
