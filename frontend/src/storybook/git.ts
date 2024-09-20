/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject, Subject } from 'rxjs';
import { GitModel } from 'src/app/openapi';
import {
  GetGitModel,
  GitModelService,
} from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';

export const mockPrimaryGitModel: Readonly<GitModel> = {
  id: 1,
  primary: true,
  path: 'fakePath',
  revision: 'fakeRevision',
  entrypoint: 'fakeEntrypoint',
  password: false,
  username: 'fakeUsername',
  repository_id: null,
};

export class MockGitModelService implements Partial<GitModelService> {
  private _gitModel = new Subject<GetGitModel | undefined>();
  private _gitModels = new BehaviorSubject<GetGitModel[] | undefined>(
    undefined,
  );

  public readonly gitModel$ = this._gitModel.asObservable();
  public readonly gitModels$ = this._gitModels.asObservable();

  constructor(gitModel: GetGitModel, gitModels: GetGitModel[]) {
    this._gitModel.next(gitModel);
    this._gitModels.next(gitModels);
  }

  reset() {} // eslint-disable-line @typescript-eslint/no-empty-function
}
