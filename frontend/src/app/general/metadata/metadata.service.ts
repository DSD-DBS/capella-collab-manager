/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { compare } from 'semver';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import {
  Metadata,
  MetadataService as OpenAPIMetadataService,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class MetadataService {
  constructor(
    private httpClient: HttpClient,
    private localStorageService: LocalStorageService,
    public dialog: MatDialog,
    private metadataService: OpenAPIMetadataService,
  ) {
    this.loadVersion();
    this.loadBackendMetadata().subscribe();
  }

  public version: Version | undefined;
  public oldVersion: string | undefined;
  public changedVersion = false;

  private _backendMetadata = new BehaviorSubject<Metadata | undefined>(
    undefined,
  );
  readonly backendMetadata = this._backendMetadata.asObservable();

  loadVersion(): void {
    if (!this.version) {
      this.httpClient
        .get<Version>('assets/version.json')
        .subscribe((version: Version) => {
          this.version = version;
          this.determinateChangedVersion();
        });
    }
  }

  loadBackendMetadata(): Observable<Metadata> {
    return this.metadataService
      .getMetadata()
      .pipe(tap((metadata: Metadata) => this._backendMetadata.next(metadata)));
  }

  determinateChangedVersion() {
    this.oldVersion = this.localStorageService.getValue('version');
    if (this.oldVersion != this.version?.git.tag) {
      this.changedVersion = true;
    }
  }

  clickedOnVersionNotes() {
    this.localStorageService.setValue('version', this.version!.git.tag);
    this.changedVersion = false;
  }

  compareFrontendVersionWithCurrent(version: string): number {
    /**
     * Compares a version with the current version
     * @param  {string} version  Version to compare with.
     * @return {number}          1 if version is higher, 0 if versions are equal, -1 if version is lower, -2 if error
     */
    if (this.version?.git.tag) {
      return this.compareFrontendVersions(version, this.version?.git.tag);
    } else {
      return -2;
    }
  }

  compareFrontendVersionWithOld(version: string) {
    if (this.oldVersion) {
      return this.compareFrontendVersions(version, this.oldVersion);
    } else {
      return -2;
    }
  }

  private compareFrontendVersions(version1: string, version2: string) {
    return compare(version1, version2);
  }
}

export interface GitVersion {
  version: string;
  tag: string;
}

export interface Version {
  git: GitVersion;
}
