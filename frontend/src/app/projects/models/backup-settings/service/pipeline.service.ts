/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { SimpleT4CModel } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { BaseGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PipelineService {
  constructor(
    private http: HttpClient,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  private _pipelines = new BehaviorSubject<Pipeline[] | undefined>(undefined);
  private _pipeline = new BehaviorSubject<Pipeline | undefined>(undefined);

  public readonly pipelines$ = this._pipelines.asObservable();
  public readonly pipeline$ = this._pipeline.asObservable();

  urlFactory(projectSlug: string, modelSlug: string): string {
    return `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/backups/pipelines`;
  }

  loadPipelines(
    projectSlug: string,
    modelSlug: string,
  ): Observable<Pipeline[]> {
    this._pipelines.next(undefined);
    return this.http
      .get<Pipeline[]>(this.urlFactory(projectSlug, modelSlug))
      .pipe(
        tap((pipelines: Pipeline[]) => {
          this._pipelines.next(pipelines);
        }),
      );
  }

  resetPipeline() {
    this._pipeline.next(undefined);
  }

  resetPipelines() {
    this._pipelines.next(undefined);
  }

  loadPipeline(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
  ): Observable<Pipeline> {
    this._pipeline.next(undefined);
    return this.http
      .get<Pipeline>(`${this.urlFactory(projectSlug, modelSlug)}/${pipelineID}`)
      .pipe(
        tap((pipeline) => {
          this._pipeline.next(pipeline);
          this.breadcrumbsService.updatePlaceholder({ pipeline });
        }),
      );
  }

  createPipeline(
    projectSlug: string,
    modelSlug: string,
    body: PostPipeline,
  ): Observable<Pipeline> {
    return this.http.post<Pipeline>(this.urlFactory(projectSlug, modelSlug), {
      git_model_id: body.gitmodelId,
      t4c_model_id: body.t4cmodelId,
      include_commit_history: body.includeCommitHistory,
      run_nightly: body.runNightly,
    });
  }

  removePipeline(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    force: boolean,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.urlFactory(projectSlug, modelSlug)}/${pipelineID}`,
      { params: new HttpParams().set('force', String(force)) },
    );
  }
}

export type Pipeline = {
  id: number;
  t4c_model: SimpleT4CModel;
  git_model: BaseGitModel;
  run_nightly: boolean;
  include_commit_history: boolean;
};

export type PostPipeline = {
  t4cmodelId: number;
  gitmodelId: number;
  includeCommitHistory: boolean;
  runNightly: boolean;
};
