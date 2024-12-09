/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncValidatorFn } from '@angular/forms';
import { BehaviorSubject, Observable, of } from 'rxjs';
import {
  GitInstance,
  GitModel,
  GitType,
  ValidationError,
} from 'src/app/openapi';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

export const mockPrimaryGitModel: Readonly<GitModel> = {
  id: 1,
  primary: true,
  path: 'https://example.com/repository.git',
  revision: 'main',
  entrypoint: 'path/to/entrypoint',
  password: false,
  username: 'User ABC',
  repository_id: null,
};

export const mockGitLabInstance: Readonly<GitInstance> = {
  id: 1,
  name: 'GitLab example',
  url: 'https://gitlab.com',
  api_url: 'https://gitlab.com/api/v4',
  type: GitType.GitLab,
};

export const mockGitHubInstance: Readonly<GitInstance> = {
  id: 2,
  name: 'GitHub example',
  url: 'https://github.com',
  api_url: 'https://api.github.com',
  type: GitType.GitHub,
};

export const mockGitInstance: Readonly<GitInstance> = {
  id: 3,
  name: 'General example',
  url: 'https://example.com',
  api_url: null,
  type: GitType.General,
};

class MockGitModelService implements Partial<GitModelService> {
  private _gitModel = new BehaviorSubject<GitModel | undefined>(undefined);
  private _gitModels = new BehaviorSubject<GitModel[] | undefined>(undefined);

  public readonly gitModel$ = this._gitModel.asObservable();
  public readonly gitModels$ = this._gitModels.asObservable();

  constructor(gitModel: GitModel, gitModels: GitModel[]) {
    this._gitModel.next(gitModel);
    this._gitModels.next(gitModels);
  }

  reset() {} // eslint-disable-line @typescript-eslint/no-empty-function
}

export const mockGitModelServiceProvider = (
  gitModel: GitModel,
  gitModels: GitModel[],
) => {
  return {
    provide: GitModelService,
    useValue: new MockGitModelService(gitModel, gitModels),
  };
};

class MockGitInstancesService implements Partial<GitInstancesWrapperService> {
  private _gitInstances = new BehaviorSubject<GitInstance[] | undefined>(
    undefined,
  );
  private _gitInstance = new BehaviorSubject<GitInstance | undefined>(
    undefined,
  );

  public readonly gitInstances$ = this._gitInstances.asObservable();
  public readonly gitInstance$ = this._gitInstance.asObservable();

  constructor(
    gitInstance?: GitInstance | undefined,
    gitInstances?: GitInstance[] | undefined,
  ) {
    this._gitInstance.next(gitInstance);
    this._gitInstances.next(gitInstances);
  }

  asyncNameValidator(): AsyncValidatorFn {
    return (): Observable<ValidationError | null> => {
      return of(null);
    };
  }

  loadGitInstances(): void {} // eslint-disable-line @typescript-eslint/no-empty-function
}

export const mockGitInstancesServiceProvider = (
  gitInstance?: GitInstance | undefined,
  gitInstances?: GitInstance[] | undefined,
) => {
  return {
    provide: GitInstancesWrapperService,
    useValue: new MockGitInstancesService(gitInstance, gitInstances),
  };
};
