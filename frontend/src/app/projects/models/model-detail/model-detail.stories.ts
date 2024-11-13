/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockGitModelServiceProvider,
  mockPrimaryGitModel,
} from 'src/storybook/git';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import { mockT4CModel, mockT4CModelServiceProvider } from 'src/storybook/t4c';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { ModelDetailComponent } from './model-detail.component';

const meta: Meta<ModelDetailComponent> = {
  title: 'Model Components/Model Sources/Overview',
  component: ModelDetailComponent,
};

export default meta;
type Story = StoryObj<ModelDetailComponent>;

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(mockModel, [])],
    }),
  ],
};

export const LoadingAsAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, []),
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
      ],
    }),
  ],
};

export const WithRepositoryAsAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockModelWrapperServiceProvider(mockModel, []),
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
        mockGitModelServiceProvider(mockPrimaryGitModel, [
          mockPrimaryGitModel,
          { ...mockPrimaryGitModel, id: 2, primary: false, username: '' },
        ]),
        mockT4CModelServiceProvider(mockT4CModel, [mockT4CModel]),
      ],
    }),
  ],
};
