/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import {
  mockGitInstance,
  mockGitInstancesServiceProvider,
  mockGitModelServiceProvider,
  mockPrimaryGitModel,
} from 'src/storybook/git';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import {
  mockProject,
  mockProjectWrapperServiceProvider,
} from 'src/storybook/project';
import { mockActivatedRouteProvider } from 'src/storybook/routes';
import { ManageGitModelComponent } from './manage-git-model.component';

const meta: Meta<ManageGitModelComponent> = {
  title: 'Model Components/Model Sources/Git',
  component: ManageGitModelComponent,
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
type Story = StoryObj<ManageGitModelComponent>;

export const InvalidURL: Story = {
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const absoluteURL = canvas.getByTestId('absolute-url');
    const resultingURL = canvas.getByTestId('resulting-url');
    await userEvent.type(absoluteURL, 'invalid-url');
    await userEvent.click(absoluteURL);
    await userEvent.click(resultingURL);
  },
};

export const ValidURL: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const absoluteURL = canvas.getByTestId('absolute-url');
    const resultingURL = canvas.getByTestId('resulting-url');
    await userEvent.type(absoluteURL, 'https://example.com');
    await userEvent.click(absoluteURL);
    await userEvent.click(resultingURL);
  },
};

export const ExistingGitModel: Story = {
  args: {
    resultUrl: 'https://example.com',
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockGitModelServiceProvider(mockPrimaryGitModel, []),
        mockActivatedRouteProvider({
          'git-model': '-1',
        }),
        mockGitInstancesServiceProvider(undefined, [mockGitInstance]),
      ],
    }),
  ],
};

export const ExistingGitModelEditing: Story = {
  args: {
    resultUrl: 'https://example.com',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByTestId('edit'));
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockGitModelServiceProvider(mockPrimaryGitModel, []),
        mockActivatedRouteProvider({
          'git-model': '-1',
        }),
        mockGitInstancesServiceProvider(undefined, [mockGitInstance]),
      ],
    }),
  ],
};
