/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { SimpleT4CModel } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { BaseGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PipelineService {
  constructor(private http: HttpClient) {}

  _pipelines = new BehaviorSubject<Pipeline[] | undefined>(undefined);
  _pipeline = new BehaviorSubject<Pipeline | undefined>(undefined);

  pipelines = this._pipelines.asObservable();
  pipeline = this._pipeline.asObservable();

  loading: boolean = false;

  getBackups(project: string, modelSlug: string): Observable<Pipeline[]> {
    this.loading = true;
    return this.http
      .get<Pipeline[]>(
        `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines`
      )
      .pipe(
        tap((pipelines: Pipeline[]) => {
          this.loading = false;
          this._pipelines.next(pipelines);
        })
      );
  }

  resetPipeline() {
    this._pipeline.next(undefined);
  }

  resetPipelines() {
    this._pipelines.next(undefined);
  }

  getPipeline(
    project: string,
    modelSlug: string,
    pipelineID: number
  ): Observable<Pipeline> {
    this.loading = true;
    return this.http.get<Pipeline>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines/${pipelineID}`
    );
  }

  createBackup(
    project: string,
    modelSlug: string,
    body: PostPipeline
  ): Observable<Pipeline> {
    return this.http.post<Pipeline>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines`,
      {
        git_model_id: body.gitmodelId,
        t4c_model_id: body.t4cmodelId,
        include_commit_history: body.includeCommitHistory,
        run_nightly: body.runNightly,
      }
    );
  }

  removeBackup(
    project: string,
    modelSlug: string,
    backupId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines/${backupId}`
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
