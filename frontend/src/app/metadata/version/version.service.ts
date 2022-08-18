/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { ReleaseNote } from '../release-notes/release-note.service';

@Injectable({
  providedIn: 'root',
})
export class VersionService {
  constructor(private httpClient: HttpClient) {}

  loadVersion(): Observable<Version> {
    return this.httpClient.get<Version>('assets/version.json');
  }

  loadBackendMetadata(): Observable<BackendMetadata> {
    return this.httpClient.get<BackendMetadata>(
      environment.backend_url + '/metadata'
    );
  }
}

export interface GitVersion {
  version: string;
  tag: string;
}

export interface Version {
  git: GitVersion;
  github: Array<ReleaseNote>;
}

export interface BackendMetadata {
  version: string;
  tag: string;
}
