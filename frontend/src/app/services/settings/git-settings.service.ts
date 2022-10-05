/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, Subject, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitSettingsService {
  private BACKEND_URL_PREFIX =
    environment.backend_url + '/settings/modelsources/git/';
  private baseUrl = new URL(
    '/settings/modelsources/git',
    environment.backend_url + '/'
  );

  private _gitSettings = new BehaviorSubject<GitSettings[]>([]);
  private _gitSetting = new Subject<GitSettings>();

  readonly gitSettings = this._gitSettings.asObservable();
  readonly gitSetting = this._gitSetting.asObservable();

  constructor(private http: HttpClient) {}

  loadGitSettings(): void {
    this.http.get<GitSettings[]>(this.BACKEND_URL_PREFIX).subscribe({
      next: (gitSettings) => this._gitSettings.next(gitSettings),
    });
  }

  loadGitSettingById(id: number): void {
    this.http.get<GitSettings>(this.BACKEND_URL_PREFIX + id).subscribe({
      next: (gitSetting) => this._gitSetting.next(gitSetting),
    });
  }

  createGitSettings(gitSetting: {
    name: string;
    url: string;
    type: GitType;
  }): Observable<GitSettings> {
    return this.http
      .post<GitSettings>(this.BACKEND_URL_PREFIX, gitSetting)
      .pipe(tap(() => this.loadGitSettings()));
  }

  editGitSettings(
    id: number,
    name: string,
    url: string,
    type: GitType
  ): Observable<GitSettings> {
    return this.http
      .put<GitSettings>(this.BACKEND_URL_PREFIX + id, {
        type: type,
        name: name,
        url: url,
      })
      .pipe(tap(() => this.loadGitSettings()));
  }

  deleteGitSettings(id: number) {
    return this.http
      .delete(this.BACKEND_URL_PREFIX + id)
      .pipe(tap(() => this.loadGitSettings()));
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
