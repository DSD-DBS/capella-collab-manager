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
import {
  SimpleT4CModel,
  T4CInstance,
  T4CLicenseServer,
  T4CModel,
  T4CRepository,
  T4CRepositoryStatus,
  ValidationError,
} from 'src/app/openapi';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import {
  ExtendedT4CRepository,
  T4CRepositoryWrapperService,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { mockToolVersion } from 'src/storybook/tool';
import { T4CLicenseServerWrapperService } from '../app/services/settings/t4c-license-server.service';

export const mockTeamForCapellaRepository: Readonly<SimpleT4CModel> = {
  project_name: 'project',
  repository_name: 'repository',
  instance_name: 'instance',
};

export const mockT4CInstance: Readonly<T4CInstance> = {
  id: 1,
  name: 'test',
  host: 'localhost',
  port: 2036,
  cdo_port: 12036,
  http_port: 8080,
  license_server: {
    id: 1,
    name: 'licenseServer',
    license_key: 'licenseKey',
    usage_api: 'http://example.com',
  },
  rest_api: 'http://localhost:8081/api/v1.0',
  username: 'admin',
  protocol: 'ws',
  version: mockToolVersion,
  is_archived: false,
};

export const mockT4CRepository: Readonly<T4CRepository> = {
  id: 1,
  name: 'repository',
  instance: mockT4CInstance,
  status: T4CRepositoryStatus.Online,
};

export const mockExtendedT4CRepository: Readonly<ExtendedT4CRepository> = {
  id: 1,
  name: 'repository',
  instance: mockT4CInstance,
  status: 'LOADING',
};

export const mockT4CModel: Readonly<T4CModel> = {
  id: 1,
  name: 'project',
  repository: mockT4CRepository,
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

  resetT4CInstance(): void {} // eslint-disable-line @typescript-eslint/no-empty-function
}

export const mockT4CLicenseServer: Readonly<T4CLicenseServer> = {
  id: 1,
  name: 'licenseServer',
  license_key: 'licenseKey',
  usage_api: 'http://example.com',
  usage: {
    free: 1,
    total: 2,
  },
  license_server_version: '1.0.2324234',
  instances: [mockT4CInstance],
  warnings: [],
};

export const mockT4CLicenseServerUnreachable: Readonly<T4CLicenseServer> = {
  ...mockT4CLicenseServer,
  usage: null,
  license_server_version: null,
};

export const mockT4CLicenseServerUnused: Readonly<T4CLicenseServer> = {
  ...mockT4CLicenseServer,
  instances: [],
};

export class MockT4CLicenseServerWrapperService
  implements Partial<T4CLicenseServerWrapperService>
{
  private _licenseServer = new BehaviorSubject<T4CLicenseServer | undefined>(
    undefined,
  );
  public readonly licenseServer$ = this._licenseServer.asObservable();

  private _licenseServers = new BehaviorSubject<T4CLicenseServer[] | undefined>(
    undefined,
  );
  public readonly licenseServers$ = this._licenseServers.asObservable();

  constructor(
    licenseServer: T4CLicenseServer,
    licenseServers: T4CLicenseServer[],
  ) {
    this._licenseServer.next(licenseServer);
    this._licenseServers.next(licenseServers);
  }

  asyncNameValidator(_ignoreServer?: T4CLicenseServer): AsyncValidatorFn {
    return (_control: AbstractControl): Observable<ValidationError | null> => {
      return of(null);
    };
  }

  resetLicenseServer(): void {} // eslint-disable-line @typescript-eslint/no-empty-function
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

  reset() {} // eslint-disable-line @typescript-eslint/no-empty-function
  loadRepositories() {} // eslint-disable-line @typescript-eslint/no-empty-function

  asyncNameValidator(): AsyncValidatorFn {
    return (_control: AbstractControl): Observable<ValidationErrors | null> => {
      return of(null);
    };
  }
}

export class MockT4CModelService implements Partial<T4CModelService> {
  private _t4cModel = new BehaviorSubject<T4CModel | undefined>(undefined);
  public readonly t4cModel$ = this._t4cModel.asObservable();

  private _t4cModels = new BehaviorSubject<T4CModel[] | undefined>(undefined);
  public readonly t4cModels$ = this._t4cModels.asObservable();

  compatibleT4CInstances$: Observable<T4CInstance[] | undefined> =
    of(undefined);

  reset() {} // eslint-disable-line @typescript-eslint/no-empty-function

  constructor(
    t4cModel: T4CModel | undefined,
    t4cModels: T4CModel[] | undefined,
    t4cInstances: T4CInstance[] | undefined = undefined,
  ) {
    this._t4cModel.next(t4cModel);
    this._t4cModels.next(t4cModels);
    this.compatibleT4CInstances$ = of(t4cInstances);
  }
}
