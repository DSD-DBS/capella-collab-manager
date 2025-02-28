/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { computed, signal } from '@angular/core';
import {
  Version,
  VersionService,
  ViewedVersion,
} from '../app/general/metadata/version/version.service';

export const mockVersion: Version = {
  git: {
    version: 'v1.0.0',
    tag: 'v1.0.0',
    branch: 'main',
    commit: '98eac08babf1f6f37932642faf887b6955fb434c',
    date: '2021-04-30T14:00:00+00:00',
  },
  build: {
    date: '2021-04-30T14:00:00+00:00',
  },
};

export const mockBackendVersion = '1.0.0';
export const mockViewedVersion: ViewedVersion = {
  frontend: 'v1.0.0',
  backend: 'v1.0.0',
};

export class MockVersionService implements Partial<VersionService> {
  public viewedVersion = signal<ViewedVersion | null>(null);
  public versionMeta = signal<Version | null>(null);
  public backendVersion = signal<string | null>(null);
  public frontendVersion = computed(() => {
    if (this.versionMeta()) {
      return this.versionMeta()!.git.version;
    } else {
      return null;
    }
  });

  public showBothVersions = computed(() => {
    return this.backendVersion() !== this.frontendVersion();
  });

  public versionsHaveChanged = computed(() => {
    if (
      !this.viewedVersion() ||
      !this.frontendVersion() ||
      !this.backendVersion()
    ) {
      return false;
    }
    return (
      this.viewedVersion()!.frontend !== this.frontendVersion() ||
      this.viewedVersion()!.backend !== this.backendVersion()
    );
  });

  constructor(
    version: Version,
    backendVersion: string,
    viewedVersion: ViewedVersion,
  ) {
    this.versionMeta.set(version);
    this.backendVersion.set(backendVersion);
    this.viewedVersion.set(viewedVersion);
  }
}

export const mockVersionServiceProvider = (
  version: Version,
  backendVersion: string,
  viewedVersion: ViewedVersion,
) => {
  return {
    provide: VersionService,
    useValue: new MockVersionService(version, backendVersion, viewedVersion),
  };
};
