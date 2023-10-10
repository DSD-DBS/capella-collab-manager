/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, Observable, map, take, tap } from 'rxjs';
import {
  T4CInstance,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-instance.service';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(
    private http: HttpClient,
    private t4cInstanceService: T4CInstanceService,
  ) {}

  private _repositories = new BehaviorSubject<
    T4CServerRepository[] | undefined
  >(undefined);

  public readonly repositories$ = this._repositories.asObservable();

  urlFactory(instanceId: number, repositoryId: number): string {
    return `${this.t4cInstanceService.urlFactory(
      instanceId,
    )}/repositories/${repositoryId}`;
  }

  loadRepositories(instanceId: number): void {
    this.http
      .get<T4CServerRepository[]>(
        `${this.t4cInstanceService.urlFactory(instanceId)}/repositories/`,
      )
      .subscribe({
        next: (repositories) => this._repositories.next(repositories),
        error: () => this._repositories.next(undefined),
      });
  }

  refreshRepositories(instanceId: number): void {
    const updateRepositories = this._repositories.value?.map((repository) => {
      return { ...repository, status: 'LOADING' } as T4CServerRepository;
    });
    this._repositories.next(updateRepositories);
    this.loadRepositories(instanceId);
  }

  createRepository(
    instanceId: number,
    repository: CreateT4CRepository,
  ): Observable<T4CRepository> {
    return this.http
      .post<T4CRepository>(
        `${this.t4cInstanceService.urlFactory(instanceId)}/repositories/`,
        repository,
      )
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  startRepository(instanceId: number, repositoryId: number): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.http
      .post<null>(`${this.urlFactory(instanceId, repositoryId)}/start/`, {})
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  stopRepository(instanceId: number, repositoryId: number): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.http
      .post<null>(`${this.urlFactory(instanceId, repositoryId)}/stop/`, {})
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  recreateRepository(
    instanceId: number,
    repositoryId: number,
  ): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.http
      .post<null>(`${this.urlFactory(instanceId, repositoryId)}/recreate/`, {})
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  deleteRepository(instanceId: number, repositoryId: number): Observable<null> {
    return this.http
      .delete<null>(`${this.urlFactory(instanceId, repositoryId)}/`)
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  asyncNameValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.repositories$.pipe(
        take(1),
        map((t4cRepositories) => {
          const nameExists = t4cRepositories?.find(
            (instance) => instance.name === control.value,
          );
          return nameExists ? { uniqueName: { value: control.value } } : null;
        }),
      );
    };
  }

  reset(): void {
    this._repositories.next(undefined);
  }

  private publishRepositoriesWithChangedStatus(
    repositoryId: number,
    status: string,
  ): void {
    const currentRepositories = this._repositories.value;

    const updatedRepositories = currentRepositories?.map((repository) => {
      if (repository.id === repositoryId) {
        return { ...repository, status: status } as T4CServerRepository;
      }
      return repository;
    });
    this._repositories.next(updatedRepositories);
  }
}

export type CreateT4CRepository = {
  name: string;
};

export type T4CRepository = CreateT4CRepository & {
  id: number;
  instance: T4CInstance;
};

export type T4CServerRepository = T4CRepository & {
  status:
    | 'ONLINE'
    | 'OFFLINE'
    | 'INITIAL'
    | 'INSTANCE_UNREACHABLE'
    | 'NOT_FOUND'
    | 'LOADING';
};
