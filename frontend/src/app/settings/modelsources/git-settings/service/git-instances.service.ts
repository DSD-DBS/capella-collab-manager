/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class GitInstancesService {
  private BACKEND_URL_PREFIX =
    environment.backend_url + '/settings/modelsources/git';

  private _gitInstances = new BehaviorSubject<GitInstance[] | undefined>(
    undefined,
  );
  private _gitInstance = new BehaviorSubject<GitInstance | undefined>(
    undefined,
  );

  public readonly gitInstances$ = this._gitInstances.asObservable();
  public readonly gitInstance$ = this._gitInstance.asObservable();

  constructor(private http: HttpClient) {}

  loadGitInstances(): void {
    this.http
      .get<BackendBasicGitInstance[]>(this.BACKEND_URL_PREFIX)
      .pipe(
        map((backendGitInstances) => {
          return backendGitInstances.map((backendGitInstance) =>
            this.transformGitInstance(backendGitInstance),
          );
        }),
      )
      .subscribe((gitInstance) => this._gitInstances.next(gitInstance));
  }

  transformGitInstance(
    backendGitInstance: BackendBasicGitInstance,
  ): GitInstance {
    const gitInstance = JSON.parse(JSON.stringify(backendGitInstance));

    gitInstance.apiURL = gitInstance.api_url;
    return gitInstance;
  }

  loadGitInstanceById(id: number): void {
    this.http
      .get<GitInstance>(this.BACKEND_URL_PREFIX + '/' + id)
      .subscribe((gitInstance) => this._gitInstance.next(gitInstance));
  }

  createGitInstance(gitInstance: BasicGitInstance): Observable<GitInstance> {
    return this.http
      .post<GitInstance>(this.BACKEND_URL_PREFIX, {
        name: gitInstance.name,
        url: gitInstance.url,
        type: gitInstance.type,
        api_url: gitInstance.apiURL,
      })
      .pipe(tap(() => this.loadGitInstances()));
  }

  editGitInstance(gitInstance: GitInstance): Observable<GitInstance> {
    return this.http
      .patch<GitInstance>(this.BACKEND_URL_PREFIX + '/' + gitInstance.id, {
        type: gitInstance.type,
        name: gitInstance.name,
        url: gitInstance.url,
        api_url: gitInstance.apiURL,
      })
      .pipe(tap(() => this.loadGitInstances()));
  }

  deleteGitInstance(id: number) {
    return this.http
      .delete(this.BACKEND_URL_PREFIX + '/' + id)
      .pipe(tap(() => this.loadGitInstances()));
  }

  asyncNameValidator(ignoreInstance?: GitInstance): AsyncValidatorFn {
    const ignoreId = ignoreInstance ? ignoreInstance.id : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.gitInstances$.pipe(
        take(1),
        map((gitInstances) => {
          const nameExists = gitInstances?.find(
            (instance) =>
              instance.name === control.value && instance.id != ignoreId,
          );
          return nameExists ? { uniqueName: { value: control.value } } : null;
        }),
      );
    };
  }
}

export interface BackendBasicGitInstance {
  id: number;
  name: string;
  url: string;
  api_url?: string;
  type: GitType;
}

export type BasicGitInstance = Omit<GitInstance, 'id'>;

export interface GitInstance {
  id: number;
  name: string;
  url: string;
  apiURL?: string;
  type: GitType;
}

export type GitType = 'general' | 'gitlab' | 'github' | 'azuredevops';

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
