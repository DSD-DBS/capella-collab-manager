/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { mockActivatedRouteProvider } from 'src/storybook/routes';
import {
  mockT4CInstance,
  mockT4CInstanceWrapperServiceProvider,
  mockT4CLicenseServer,
  mockT4CLicenseServerWrapperServiceProvider,
} from 'src/storybook/t4c';
import { mockCapellaToolVersion } from 'src/storybook/tool';
import { EditT4CInstanceComponent } from './edit-t4c-instance.component';

const meta: Meta<EditT4CInstanceComponent> = {
  title: 'Settings Components/Modelsources/T4C/Server Instance',
  component: EditT4CInstanceComponent,
  args: {
    capellaVersions: [mockCapellaToolVersion],
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CLicenseServerWrapperServiceProvider(mockT4CLicenseServer, [
          mockT4CLicenseServer,
        ]),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<EditT4CInstanceComponent>;

export const AddInstance: Story = {
  args: {},
};

export const ExistingInstance: Story = {
  args: {
    existing: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CInstanceWrapperServiceProvider(mockT4CInstance, [
          mockT4CInstance,
        ]),
        mockActivatedRouteProvider({
          instance: -1,
        }),
      ],
    }),
  ],
};

export const EditExistingInstance: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CInstanceWrapperServiceProvider(mockT4CInstance, [
          mockT4CInstance,
        ]),
        mockActivatedRouteProvider({
          instance: -1,
        }),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const editButton = canvas.getByTestId('edit-button');
    await userEvent.click(editButton);
  },
};

export const ArchivedInstance: Story = {
  args: {
    isArchived: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CInstanceWrapperServiceProvider(mockT4CInstance, [
          mockT4CInstance,
        ]),
        mockActivatedRouteProvider({
          instance: -1,
        }),
      ],
    }),
  ],
};
