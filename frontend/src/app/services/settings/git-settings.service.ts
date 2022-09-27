/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, tap } from 'rxjs';
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
  private dataStore: { gitSettings: GitSettings[] } = { gitSettings: [] };

  readonly gitSettings = this._gitSettings.asObservable();

  constructor(private http: HttpClient) {}

  loadGitSettings(): void {
    this.http.get<GitSettings[]>(this.BACKEND_URL_PREFIX).subscribe({
      next: (gitSettings) => {
        this.dataStore.gitSettings = gitSettings;
        this._gitSettings.next(Object.assign({}, this.dataStore).gitSettings);
      },
    });
  }

  getGitSetting(): Observable<GitSettings[]> {
    return this.http.get<GitSettings[]>(this.BACKEND_URL_PREFIX);
  }

  getGitSettingById(id: number): Observable<GitSettings> {
    return this.http.get<GitSettings>(this.BACKEND_URL_PREFIX + id);
  }

  createGitSettings(
    name: string,
    url: string,
    type: GitType
  ): Observable<GitSettings> {
    return this.http
      .post<GitSettings>(this.BACKEND_URL_PREFIX, {
        type: type,
        name: name,
        url: url,
      })
      .pipe(
        tap((gitSetting) => {
          this.storeGitSetting(gitSetting);
          this.refreshGitSettings();
        })
      );
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
      .pipe(
        tap((gitSetting) => {
          this.removeGitSettingById(id);
          this.storeGitSetting(gitSetting);
          this.refreshGitSettings();
        })
      );
  }

  deleteGitSettings(id: number) {
    return this.http.delete(this.BACKEND_URL_PREFIX + id).pipe(
      tap((_) => {
        this.removeGitSettingById(id);
        this.refreshGitSettings();
      })
    );
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

  private refreshGitSettings() {
    this._gitSettings.next(Object.assign({}, this.dataStore).gitSettings);
  }

  private storeGitSetting(gitSetting: GitSettings): void {
    this.dataStore.gitSettings.push(gitSetting);
  }

  private removeGitSettingById(id: number) {
    this.dataStore.gitSettings = this.dataStore.gitSettings.filter(
      (gitSetting) => {
        return gitSetting.id != id;
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
