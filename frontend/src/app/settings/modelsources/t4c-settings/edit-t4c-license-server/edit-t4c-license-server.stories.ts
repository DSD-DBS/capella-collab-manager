/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockT4CLicenseServer,
  mockT4CLicenseServerUnreachable,
  mockT4CLicenseServerUnused,
  mockT4CLicenseServerWrapperServiceProvider,
} from '../../../../../storybook/t4c';
import { EditT4cLicenseServerComponent } from './edit-t4c-license-server.component';

const meta: Meta<EditT4cLicenseServerComponent> = {
  title: 'Settings Components/Modelsources/T4C/License Server',
  component: EditT4cLicenseServerComponent,
};

export default meta;
type Story = StoryObj<EditT4cLicenseServerComponent>;

export const AddLicenseServer: Story = {
  args: {},
};

export const ExistingLicenseServer: Story = {
  args: {
    existing: true,
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

export const ExistingUnreachableLicenseServer: Story = {
  args: {
    existing: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CLicenseServerWrapperServiceProvider(
          mockT4CLicenseServerUnreachable,
          [mockT4CLicenseServerUnreachable],
        ),
      ],
    }),
  ],
};

export const ExistingUnusedLicenseServer: Story = {
  args: {
    existing: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CLicenseServerWrapperServiceProvider(mockT4CLicenseServerUnused, [
          mockT4CLicenseServerUnused,
        ]),
      ],
    }),
  ],
};
