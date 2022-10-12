/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface Credentials {
  username: string;
  password: string;
}

export interface Revisions {
  branches: string[];
  tags: string[];
}

@Injectable({
  providedIn: 'root',
})
export class GitService {
  BACKEND_URL_PREFIX = environment.backend_url;
  base_url = new URL(environment.backend_url);

  private _revisions = new BehaviorSubject<Revisions | undefined>(undefined);

  readonly revisions = this._revisions.asObservable();

  constructor(private http: HttpClient) {}

  loadRevisions(gitUrl: string, credentials: Credentials): void {
    this.http
      .post<Revisions>(
        this.base_url.toString() + '/settings/modelsources/git/revisions',
        {
          credentials: credentials,
          url: gitUrl,
        }
      )
      .subscribe((revisions) => this._revisions.next(revisions));
  }
}
