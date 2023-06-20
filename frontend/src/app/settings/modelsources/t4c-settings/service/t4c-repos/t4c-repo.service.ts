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
import { T4CInstance } from 'src/app/services/settings/t4c-instance.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient) {}

  private _repositories = new BehaviorSubject<
    T4CServerRepository[] | undefined
  >(undefined);

  readonly repositories = this._repositories.asObservable();

  backendURLFactory(instance_id: number): string {
    return `${environment.backend_url}/settings/modelsources/t4c/${instance_id}/repositories/`;
  }

  loadRepositories(instance_id: number): void {
    this.http
      .get<T4CServerRepository[]>(this.backendURLFactory(instance_id))
      .subscribe({
        next: (repositories) => this._repositories.next(repositories),
        error: () => this._repositories.next(undefined),
      });
  }

  refreshRepositories(instance_id: number): void {
    const updateRepositories = this._repositories.value?.map((repository) => {
      return { ...repository, status: 'LOADING' } as T4CServerRepository;
    });
    this._repositories.next(updateRepositories);
    this.loadRepositories(instance_id);
  }

  createRepository(
    instance_id: number,
    repository: CreateT4CRepository
  ): Observable<T4CRepository> {
    return this.http
      .post<T4CRepository>(this.backendURLFactory(instance_id), repository)
      .pipe(tap(() => this.loadRepositories(instance_id)));
  }

  startRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repository_id, 'LOADING');
    return this.http
      .post<null>(
        `${this.backendURLFactory(instance_id)}${repository_id}/start/`,
        {}
      )
      .pipe(tap(() => this.loadRepositories(instance_id)));
  }

  stopRepository(instance_id: number, repository_id: number): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repository_id, 'LOADING');
    return this.http
      .post<null>(
        `${this.backendURLFactory(instance_id)}${repository_id}/stop/`,
        {}
      )
      .pipe(tap(() => this.loadRepositories(instance_id)));
  }

  recreateRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repository_id, 'LOADING');
    return this.http
      .post<null>(
        `${this.backendURLFactory(instance_id)}${repository_id}/recreate/`,
        {}
      )
      .pipe(tap(() => this.loadRepositories(instance_id)));
  }

  deleteRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    return this.http
      .delete<null>(`${this.backendURLFactory(instance_id)}${repository_id}/`)
      .pipe(tap(() => this.loadRepositories(instance_id)));
  }

  asyncNameValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.repositories.pipe(
        take(1),
        map((t4cRepositories) => {
          const nameExists = t4cRepositories?.find(
            (instance) => instance.name === control.value
          );
          return nameExists ? { uniqueName: { value: control.value } } : null;
        })
      );
    };
  }

  reset(): void {
    this._repositories.next(undefined);
  }

  private publishRepositoriesWithChangedStatus(
    repository_id: number,
    status: string
  ): void {
    const currentRepositories = this._repositories.value;

    const updatedRepositories = currentRepositories?.map((repository) => {
      if (repository.id === repository_id) {
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
