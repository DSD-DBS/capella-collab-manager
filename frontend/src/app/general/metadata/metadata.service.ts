/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { map } from 'rxjs';
import { UnifiedConfigWrapperService } from '../../services/unified-config-wrapper/unified-config-wrapper.service';

@Injectable({
  providedIn: 'root',
})
export class MetadataService {
  constructor(
    private httpClient: HttpClient,
    public dialog: MatDialog,
    private unifiedConfigWrapperService: UnifiedConfigWrapperService,
  ) {
    this.loadVersion();
  }

  public version: Version | undefined;
  public oldVersion: string | undefined;

  readonly backendMetadata =
    this.unifiedConfigWrapperService.unifiedConfig$.pipe(
      map((unifiedConfig) => unifiedConfig?.metadata),
    );

  loadVersion(): void {
    if (!this.version) {
      this.httpClient
        .get<Version>('version.json?_=' + new Date().getTime())
        .subscribe((version: Version) => {
          this.version = version;
        });
    }
  }

  get changedVersion(): boolean {
    const currentVersion = localStorage.getItem('version');

    return currentVersion !== null && currentVersion !== this.version?.git.tag;
  }

  clickedOnVersionNotes() {
    localStorage.setItem('version', this.version!.git.tag);
  }
}

export interface GitVersion {
  version: string;
  tag: string;
}

export interface Version {
  git: GitVersion;
}
