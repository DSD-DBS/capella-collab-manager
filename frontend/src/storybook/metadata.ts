/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Observable, of } from 'rxjs';
import {
  MetadataService,
  Version,
} from 'src/app/general/metadata/metadata.service';
import { Metadata } from 'src/app/openapi';

export const mockMetadata: Metadata = {
  version: '1.0.0',
  privacy_policy_url: 'https://example.com/privacy',
  imprint_url: 'https://example.com/imprint',
  provider: 'Provider',
  authentication_provider: 'Identity Provider',
  environment: 'Storybook Environment',
  host: 'localhost',
  port: '6006',
  protocol: 'http',
};

class MockMetadataService implements Partial<MetadataService> {
  public readonly backendMetadata: Observable<Metadata | undefined> =
    of(undefined);
  public version: Version | undefined;
  public oldVersion: string | undefined;
  public changedVersion = false;

  constructor(
    metadata: Metadata | undefined,
    version?: Version | undefined,
    oldVersion?: string | undefined,
    changedVersion?: boolean,
  ) {
    this.backendMetadata = of(metadata);
    this.version = version;
    this.oldVersion = oldVersion;
    if (changedVersion) this.changedVersion = changedVersion;
  }
}

export const mockMetadataServiceProvider = (
  metadata: Metadata | undefined,
  version?: Version | undefined,
  oldVersion?: string | undefined,
  changedVersion?: boolean,
) => {
  return {
    provide: MetadataService,
    useValue: new MockMetadataService(
      metadata,
      version,
      oldVersion,
      changedVersion,
    ),
  };
};
