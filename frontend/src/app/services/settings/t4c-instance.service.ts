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
import { BehaviorSubject, map, Observable, take, tap } from 'rxjs';
import {
  CreateT4CInstance,
  PatchT4CInstance,
  SettingsModelsourcesT4CInstancesService,
  T4CInstance,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class T4CInstanceWrapperService {
  constructor(
    private t4cInstanceService: SettingsModelsourcesT4CInstancesService,
  ) {}

  private _t4cInstances = new BehaviorSubject<T4CInstance[] | undefined>(
    undefined,
  );
  public readonly t4cInstances$ = this._t4cInstances.asObservable();

  private _t4cInstance = new BehaviorSubject<T4CInstance | undefined>(
    undefined,
  );
  public readonly t4cInstance$ = this._t4cInstance.asObservable();

  public readonly unarchivedT4cInstances$ = this._t4cInstances.pipe(
    map((t4cInstances) =>
      t4cInstances?.filter((t4cInstance) => !t4cInstance.is_archived),
    ),
  );

  loadInstances(): void {
    this._t4cInstances.next(undefined);
    this.t4cInstanceService.getT4cInstances().subscribe({
      next: (instances) => this._t4cInstances.next(instances),
      error: () => this._t4cInstances.next(undefined),
    });
  }

  loadInstance(instanceId: number): void {
    this.t4cInstanceService.getT4cInstance(instanceId).subscribe({
      next: (instance) => this._t4cInstance.next(instance),
      error: () => this._t4cInstance.next(undefined),
    });
  }

  createInstance(instance: CreateT4CInstance): Observable<T4CInstance> {
    return this.t4cInstanceService.createT4cInstance(instance).pipe(
      tap((instance) => {
        this._t4cInstance.next(instance);
        this.loadInstances();
      }),
    );
  }

  updateInstance(
    instanceId: number,
    instance: PatchT4CInstance,
  ): Observable<T4CInstance> {
    return this.t4cInstanceService.editT4cInstance(instanceId, instance).pipe(
      tap((instance) => {
        this._t4cInstance.next(instance);
        this.loadInstances();
      }),
    );
  }

  resetT4CInstance(): void {
    this._t4cInstance.next(undefined);
  }

  reset(): void {
    this.resetT4CInstance();
    this._t4cInstances.next(undefined);
  }

  asyncNameValidator(ignoreInstance?: T4CInstance): AsyncValidatorFn {
    const ignoreInstanceId = ignoreInstance ? ignoreInstance.id : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      const instanceName = control.value;
      return this.t4cInstances$.pipe(
        take(1),
        map((instances) => {
          return instances?.find(
            (instance) =>
              instance.name === instanceName &&
              instance.id !== ignoreInstanceId,
          )
            ? { uniqueName: { value: instanceName } }
            : null;
        }),
      );
    };
  }
}
