/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { BaseGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { SimpleT4CModel } from 'src/app/services/modelsources/t4c-model/t4c-model.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class BackupService {
  constructor(private http: HttpClient) {}

  pipelines = new BehaviorSubject<Pipeline[] | undefined>(undefined);
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
          this.pipelines.next(pipelines);
        })
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

  triggerRun(
    project: string,
    modelSlug: string,
    backupId: number,
    includeCommitHistory: boolean
  ): Observable<PipelineJob> {
    return this.http.post<PipelineJob>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines/${backupId}/runs`,
      { include_commit_history: includeCommitHistory }
    );
  }

  getLogs(
    project: string,
    backupId: number,
    modelSlug: string
  ): Observable<string> {
    return this.http.get<string>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines/${backupId}/runs/latest/logs`
    );
  }
}

export interface PipelineJob {
  id: string;
  date: string;
  state: string;
}

export interface Pipeline {
  id: number;
  lastrun: PipelineJob;
  t4c_model: SimpleT4CModel;
  git_model: BaseGitModel;
  run_nightly: boolean;
  include_commit_history: boolean;
}

export interface PostPipeline {
  t4cmodelId: number;
  gitmodelId: number;
  includeCommitHistory: boolean;
  runNightly: boolean;
}
