/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { PureVariantsComponent } from './pure-variants.component';

const meta: Meta<PureVariantsComponent> = {
  title: 'Settings Components/Pure Variants',
  component: PureVariantsComponent,
  decorators: [
    moduleMetadata({
      providers: [],
    }),
  ],
};

export default meta;
type Story = StoryObj<PureVariantsComponent>;

export const Loading: Story = {
  args: {
    loading: true,
  },
};

export const LoadingLicenseKey: Story = {
  args: {
    loadingLicenseKey: true,
  },
};

export const ExistingLicense: Story = {
  args: {
    configuration: {
      license_key_filename: 'license_key',
      license_server_url: 'http://localhost:8080',
    },
  },
};

export const UploadLicense: Story = {
  args: {},
};
