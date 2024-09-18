/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import {
  MetadataService,
  Version,
} from 'src/app/general/metadata/metadata.service';
import { VersionComponent } from 'src/app/general/metadata/version/version.component';
import { mockMetadata, MockMetadataService } from 'src/storybook/metadata';

const meta: Meta<VersionComponent> = {
  title: 'General Components/Version',
  component: VersionComponent,
};

export default meta;
type Story = StoryObj<VersionComponent>;

const version: Version = {
  git: {
    version: '1.0.0',
    tag: '1.0.0',
  },
};

export const VersionUnchanged: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MetadataService,
          useFactory: () =>
            new MockMetadataService(mockMetadata, version, 'v1.0.0', false),
        },
      ],
    }),
  ],
};

export const NewVersionAvailable: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MetadataService,
          useFactory: () =>
            new MockMetadataService(mockMetadata, version, 'v0.1.0', true),
        },
      ],
    }),
  ],
};

export const FirstTimeAccessed: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MetadataService,
          useFactory: () =>
            new MockMetadataService(mockMetadata, version, undefined, true),
        },
      ],
    }),
  ],
};
