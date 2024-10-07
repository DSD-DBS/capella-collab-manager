/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, Observable, map, take, tap } from 'rxjs';
import {
  CreateT4CRepository,
  ResponseModel,
  SettingsModelsourcesT4CInstancesService,
  T4CInstance,
  T4CRepository,
  T4CRepositoryStatus,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class T4CRepositoryWrapperService {
  constructor(
    private t4cInstanceService: SettingsModelsourcesT4CInstancesService,
  ) {}

  private _repositories = new BehaviorSubject<
    ExtendedT4CRepository[] | undefined
  >(undefined);

  public readonly repositories$ = this._repositories.asObservable();

  loadRepositories(instanceId: number): void {
    this.t4cInstanceService.listT4cRepositories(instanceId).subscribe({
      next: (repositories) => this._repositories.next(repositories.payload),
      error: () => this._repositories.next(undefined),
    });
  }

  refreshRepositories(instanceId: number): void {
    const updateRepositories = this._repositories.value?.map((repository) => {
      return { ...repository, status: 'LOADING' } as ExtendedT4CRepository;
    });
    this._repositories.next(updateRepositories);
    this.loadRepositories(instanceId);
  }

  createRepository(
    instanceId: number,
    repository: CreateT4CRepository,
  ): Observable<T4CRepository> {
    return this.t4cInstanceService
      .createT4cRepository(instanceId, repository)
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  startRepository(instanceId: number, repositoryId: number): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.t4cInstanceService
      .startT4cRepository(instanceId, repositoryId)
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  stopRepository(instanceId: number, repositoryId: number): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.t4cInstanceService
      .stopT4cRepository(instanceId, repositoryId)
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  recreateRepository(
    instanceId: number,
    repositoryId: number,
  ): Observable<null> {
    this.publishRepositoriesWithChangedStatus(repositoryId, 'LOADING');
    return this.t4cInstanceService
      .recreateT4cRepository(instanceId, repositoryId)
      .pipe(tap(() => this.loadRepositories(instanceId)));
  }

  deleteRepository(
    instanceId: number,
    repositoryId: number,
  ): Observable<ResponseModel> {
    return this.t4cInstanceService
      .deleteT4cRepository(instanceId, repositoryId)
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
        return { ...repository, status: status } as ExtendedT4CRepository;
      }
      return repository;
    });
    this._repositories.next(updatedRepositories);
  }
}

export type ExtendedT4CRepositoryStatus = T4CRepositoryStatus | 'LOADING';

export interface ExtendedT4CRepository {
  name: string;
  id: number;
  instance: T4CInstance;
  status: ExtendedT4CRepositoryStatus | null;
}
