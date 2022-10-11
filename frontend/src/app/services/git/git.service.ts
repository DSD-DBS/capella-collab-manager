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

export interface Instance {
  branches: string[];
  tags: string[];
}

@Injectable({
  providedIn: 'root',
})
export class GitService {
  BACKEND_URL_PREFIX = environment.backend_url;
  base_url = new URL(environment.backend_url);

  private _instance = new BehaviorSubject<Instance | undefined>(undefined);

  readonly instance = this._instance.asObservable();

  constructor(private http: HttpClient) {}

  loadInstance(gitUrl: string, credentials: Credentials): void {
    this.http
      .post<Instance>(
        this.base_url.toString() + '/settings/modelsources/git/revisions',
        credentials,
        { params: { url: gitUrl } }
      )
      .subscribe((instance) => this._instance.next(instance));
  }
}
