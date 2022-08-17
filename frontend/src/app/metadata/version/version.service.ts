/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ReleaseNote } from '../release-notes/release-note.service';

@Injectable({
  providedIn: 'root',
})
export class VersionService {
  constructor(private httpClient: HttpClient) {}

  loadVersion(): Observable<Version> {
    return this.httpClient.get<Version>('assets/version.json');
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
