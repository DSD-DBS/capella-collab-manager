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
import {
  GitInstance,
  PostGitInstance,
  SettingsModelsourcesGitService,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class GitInstancesWrapperService {
  private _gitInstances = new BehaviorSubject<GitInstance[] | undefined>(
    undefined,
  );
  private _gitInstance = new BehaviorSubject<GitInstance | undefined>(
    undefined,
  );

  public readonly gitInstances$ = this._gitInstances.asObservable();
  public readonly gitInstance$ = this._gitInstance.asObservable();

  constructor(
    private http: HttpClient,
    private gitInstancesService: SettingsModelsourcesGitService,
  ) {}

  loadGitInstances(): void {
    this.gitInstancesService
      .listGitInstances()
      .subscribe((gitInstance) => this._gitInstances.next(gitInstance));
  }

  loadGitInstanceById(id: number): void {
    this.gitInstancesService
      .getGitInstance(id)
      .subscribe((gitInstance) => this._gitInstance.next(gitInstance));
  }

  createGitInstance(gitInstance: PostGitInstance): Observable<GitInstance> {
    return this.gitInstancesService
      .createGitInstance(gitInstance)
      .pipe(tap(() => this.loadGitInstances()));
  }

  editGitInstance(
    id: number,
    gitInstance: PostGitInstance,
  ): Observable<GitInstance> {
    return this.gitInstancesService
      .editGitInstance(id, gitInstance)
      .pipe(tap(() => this.loadGitInstances()));
  }

  deleteGitInstance(id: number) {
    return this.gitInstancesService
      .deleteGitInstance(id)
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

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
