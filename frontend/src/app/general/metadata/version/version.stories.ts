/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { VersionComponent } from 'src/app/general/metadata/version/version.component';
import {
  mockBackendVersion,
  mockVersion,
  mockVersionServiceProvider,
  mockViewedVersion,
} from '../../../../storybook/version';

const meta: Meta<VersionComponent> = {
  title: 'General Components/Version',
  component: VersionComponent,
};

export default meta;
type Story = StoryObj<VersionComponent>;

export const VersionUnchanged: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockVersionServiceProvider(
          mockVersion,
          mockBackendVersion,
          mockViewedVersion,
        ),
      ],
    }),
  ],
};

export const NewVersionAvailable: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockVersionServiceProvider(
          {
            ...mockVersion,
            git: {
              ...mockVersion.git,
              version: 'v2.0.0',
            },
          },
          '2.0.0',
          mockViewedVersion,
        ),
      ],
    }),
  ],
};

export const DifferentFrontendBackend: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockVersionServiceProvider(mockVersion, '2.0.0', mockViewedVersion),
      ],
    }),
  ],
};
