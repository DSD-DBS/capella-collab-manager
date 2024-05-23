/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import {
  MetadataService,
  Version,
} from 'src/app/general/metadata/metadata.service';
import { VersionComponent } from 'src/app/general/metadata/version/version.component';
import { Metadata } from 'src/app/openapi';

const meta: Meta<VersionComponent> = {
  title: 'General Components / Version',
  component: VersionComponent,
};

export default meta;
type Story = StoryObj<VersionComponent>;

class MockMetadataService implements Partial<MetadataService> {
  public readonly backendMetadata: Observable<Metadata | undefined> =
    of(undefined);
  public version: Version | undefined;
  public oldVersion: string | undefined;
  public changedVersion = false;

  constructor(
    metadata: Metadata | undefined,
    version: Version | undefined,
    oldVersion: string | undefined,
    changedVersion: boolean,
  ) {
    this.backendMetadata = of(metadata);
    this.version = version;
    this.oldVersion = oldVersion;
    this.changedVersion = changedVersion;
  }
}

const metadata: Metadata = {
  version: '1.0.0',
  privacy_policy_url: 'https://example.com/privacy',
  imprint_url: 'https://example.com/imprint',
  provider: 'Provider',
  authentication_provider: 'Authentication provider',
  environment: 'Storybook Environment',
  host: 'localhost',
  port: '6006',
  protocol: 'http',
};

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
            new MockMetadataService(metadata, version, 'v1.0.0', false),
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
            new MockMetadataService(metadata, version, 'v0.1.0', true),
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
            new MockMetadataService(metadata, version, undefined, true),
        },
      ],
    }),
  ],
};
