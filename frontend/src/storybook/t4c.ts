/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { T4CInstance, ValidationError } from 'src/app/openapi';
import { SimpleT4CModel } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import {
  ExtendedT4CRepository,
  T4CRepositoryWrapperService,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { mockToolVersion } from 'src/storybook/tool';

export const mockTeamForCapellaRepository: Readonly<SimpleT4CModel> = {
  project_name: 'project',
  repository_name: 'repository',
  instance_name: 'instance',
};

export const mockT4CInstance: Readonly<T4CInstance> = {
  id: 1,
  name: 'test',
  license: 'license',
  host: 'localhost',
  port: 2036,
  cdo_port: 12036,
  http_port: 8080,
  usage_api: 'http://localhost:8086',
  rest_api: 'http://localhost:8081/api/v1.0',
  username: 'admin',
  protocol: 'ws',
  version_id: 1,
  version: mockToolVersion,
  is_archived: false,
};

export const mockExtendedT4CRepository: Readonly<ExtendedT4CRepository> = {
  id: 1,
  name: 'repository',
  instance: mockT4CInstance,
  status: 'LOADING',
};

export class MockT4CInstanceWrapperService
  implements Partial<T4CInstanceWrapperService>
{
  private _t4cInstance = new BehaviorSubject<T4CInstance | undefined>(
    undefined,
  );
  public readonly t4cInstance$ = this._t4cInstance.asObservable();

  private _t4cInstances = new BehaviorSubject<T4CInstance[] | undefined>(
    undefined,
  );
  public readonly t4cInstances$ = this._t4cInstances.asObservable();

  constructor(t4cInstance: T4CInstance, t4cInstances: T4CInstance[]) {
    this._t4cInstance.next(t4cInstance);
    this._t4cInstances.next(t4cInstances);
  }

  asyncNameValidator(_ignoreInstance?: T4CInstance): AsyncValidatorFn {
    return (_control: AbstractControl): Observable<ValidationError | null> => {
      return of(null);
    };
  }

  resetT4CInstance(): void {}
}

export class MockT4CRepositoryWrapperService
  implements Partial<T4CRepositoryWrapperService>
{
  private _repositories = new BehaviorSubject<
    ExtendedT4CRepository[] | undefined
  >(undefined);

  public readonly repositories$ = this._repositories.asObservable();

  constructor(repositories: ExtendedT4CRepository[]) {
    this._repositories.next(repositories);
  }

  reset() {}

  asyncNameValidator(): AsyncValidatorFn {
    return (_control: AbstractControl): Observable<ValidationErrors | null> => {
      return of(null);
    };
  }
}
