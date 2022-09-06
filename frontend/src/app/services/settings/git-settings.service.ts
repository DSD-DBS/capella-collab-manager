/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitSettingsService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/settings/modelsources/git/';

  listGitSettings(): Observable<GitSettings[]> {
    return this.http.get<GitSettings[]>(this.BACKEND_URL_PREFIX);
  }

  getGitSettings(id: number): Observable<GitSettings> {
    return this.http.get<GitSettings>(this.BACKEND_URL_PREFIX + id);
  }

  createGitSettings(
    name: string,
    url: string,
    type: GitType
  ): Observable<GitSettings> {
    return this.http.post<GitSettings>(this.BACKEND_URL_PREFIX, {
      type: type,
      name: name,
      url: url,
    });
  }

  editGitSettings(
    id: number,
    name: string,
    url: string,
    type: GitType
  ): Observable<GitSettings> {
    return this.http.put<GitSettings>(this.BACKEND_URL_PREFIX + id, {
      type: type,
      name: name,
      url: url,
    });
  }

  deleteGitSettings(id: number) {
    return this.http.delete(this.BACKEND_URL_PREFIX + id);
  }

  getRevisions(
    url: string,
    username: string,
    password: string
  ): Observable<GitReferences> {
    return of({
      branches: ['main', 'develop', 'staging'],
      tags: ['v0.1', 'v1.0', 'v2.0', 'v2.1'],
    });
    return this.http.get<GitReferences>(
      this.BACKEND_URL_PREFIX + 'list-repository',
      {
        params: {
          url,
          username,
          password,
        },
      }
    );
  }
}

export interface GitSettings {
  id: number;
  name: string;
  url: string;
  type: GitType;
}

export interface GitReferences {
  branches: string[];
  tags: string[];
}

export type GitType = 'general' | 'gitlab' | 'github' | 'azuredevops';

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
