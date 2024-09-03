/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BehaviorSubject, Observable, tap } from 'rxjs';
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
    public dialog: MatDialog,
    private metadataService: OpenAPIMetadataService,
  ) {
    this.loadVersion();
    this.loadBackendMetadata().subscribe();
  }

  public version: Version | undefined;
  public oldVersion: string | undefined;

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
        });
    }
  }

  loadBackendMetadata(): Observable<Metadata> {
    return this.metadataService
      .getMetadata()
      .pipe(tap((metadata: Metadata) => this._backendMetadata.next(metadata)));
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
