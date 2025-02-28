/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Observable, of } from 'rxjs';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { Metadata } from 'src/app/openapi';

export const mockMetadata: Metadata = {
  version: '1.0.0',
  privacy_policy_url: 'https://example.com/privacy',
  imprint_url: 'https://example.com/imprint',
  provider: 'Provider',
  authentication_provider: 'Identity Provider',
  host: 'localhost',
  port: '6006',
  protocol: 'http',
};

class MockMetadataService implements Partial<MetadataService> {
  public readonly backendMetadata: Observable<Metadata | undefined> =
    of(undefined);

  constructor(metadata: Metadata | undefined) {
    this.backendMetadata = of(metadata);
  }
}

export const mockMetadataServiceProvider = (metadata: Metadata | undefined) => {
  return {
    provide: MetadataService,
    useValue: new MockMetadataService(metadata),
  };
};
