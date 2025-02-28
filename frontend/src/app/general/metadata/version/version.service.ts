/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { z } from 'zod';
import { UnifiedConfigWrapperService } from '../../../services/unified-config-wrapper/unified-config-wrapper.service';

const viewedVersionSchema = z.object({
  frontend: z.string(),
  backend: z.string(),
});

export type ViewedVersion = z.infer<typeof viewedVersionSchema>;

@Injectable({
  providedIn: 'root',
})
export class VersionService {
  private unifiedConfigWrapperService = inject(UnifiedConfigWrapperService);
  private httpClient = inject(HttpClient);

  public viewedVersion = signal<ViewedVersion | null>(null);
  public versionMeta = signal<Version | null>(null);
  private unifiedConfig = toSignal(
    this.unifiedConfigWrapperService.unifiedConfig$,
  );
  public backendVersion = computed(() => {
    if (this.unifiedConfig()?.metadata?.version) {
      return `v${this.unifiedConfig()!.metadata.version}`;
    } else {
      return null;
    }
  });

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

  loadVersion(): void {
    if (!this.versionMeta()) {
      this.httpClient
        .get<Version>('version.json?_=' + new Date().getTime())
        .subscribe((version: Version) => {
          this.versionMeta.set(version);
        });
    }
  }

  loadViewedVersion(): void {
    const viewedVersion = localStorage.getItem('viewedVersion'); // TODO name
    if (viewedVersion) {
      try {
        const parsed = viewedVersionSchema.parse(JSON.parse(viewedVersion));
        this.viewedVersion.set(parsed);
      } catch {
        localStorage.removeItem('viewedVersion');
      }
    }
  }

  markVersionsAsViewed(): void {
    if (!this.frontendVersion() || !this.backendVersion()) {
      return;
    }
    this.viewedVersion.set({
      frontend: this.frontendVersion()!,
      backend: this.backendVersion()!,
    });
    localStorage.setItem('viewedVersion', JSON.stringify(this.viewedVersion()));
  }

  constructor() {
    this.loadViewedVersion();
    this.loadVersion();
  }
}

export interface GitVersion {
  version: string;
  tag: string;
  date: string;
  commit: string;
  branch: string;
}

export interface BuildMeta {
  date: string;
}

export interface Version {
  git: GitVersion;
  build: BuildMeta;
}
