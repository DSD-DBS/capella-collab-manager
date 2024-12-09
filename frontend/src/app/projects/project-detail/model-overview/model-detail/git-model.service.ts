/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject, tap } from 'rxjs';
import {
  GitModel,
  ProjectsModelsGitService,
  PutGitModel,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class GitModelService {
  constructor(private gitModelService: ProjectsModelsGitService) {}

  private _gitModel = new Subject<GitModel | undefined>();
  private _gitModels = new BehaviorSubject<GitModel[] | undefined>(undefined);

  public readonly gitModel$ = this._gitModel.asObservable();
  public readonly gitModels$ = this._gitModels.asObservable();

  loadGitModels(projectSlug: string, modelSlug: string): void {
    this.gitModelService
      .getGitModels(projectSlug, modelSlug)
      .subscribe((gitModels) => this._gitModels.next(gitModels));
  }

  loadGitModelById(
    projectSlug: string,
    modelSlug: string,
    gitModelId: number,
  ): void {
    this.gitModelService
      .getGitModelById(projectSlug, gitModelId, modelSlug)
      .subscribe((gitModel) => this._gitModel.next(gitModel));
  }

  updateGitRepository(
    projectSlug: string,
    modelSlug: string,
    gitModelId: number,
    gitModel: PutGitModel,
  ): Observable<GitModel> {
    return this.gitModelService
      .updateGitModelById(projectSlug, gitModelId, modelSlug, gitModel)
      .pipe(
        tap((gitModel) => {
          this.loadGitModels(projectSlug, modelSlug);
          this._gitModel.next(gitModel);
        }),
      );
  }

  reset() {
    this._gitModels.next(undefined);
    this._gitModel.next(undefined);
  }
}
