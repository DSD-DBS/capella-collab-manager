/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from 'src/app/services/user/user.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
@UntilDestroy()
export class PipelineRunService {
  constructor(private http: HttpClient) {}

  _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(undefined);
  pipelineRun = this._pipelineRun.asObservable();

  resetPipelineRun() {
    this._pipelineRun.next(undefined);
  }

  triggerRun(
    project: string,
    modelSlug: string,
    backupId: number,
    includeCommitHistory: boolean
  ): Observable<PipelineRun> {
    return this.http.post<PipelineRun>(
      `${environment.backend_url}/projects/${project}/models/${modelSlug}/backups/pipelines/${backupId}/runs`,
      { include_commit_history: includeCommitHistory }
    );
  }

  getPipelineRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number
  ): Observable<PipelineRun> {
    return this.http.get<PipelineRun>(
      `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/backups/pipelines/${pipelineID}/runs/${pipelineRunID}`
    );
  }

  getRunsOfPipeline(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number
  ): Observable<PipelineRun[]> {
    return this.http.get<PipelineRun[]>(
      `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/backups/pipelines/${pipelineID}/runs`
    );
  }

  getLogs(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    runID: number
  ): Observable<string> {
    return this.http.get<string>(
      `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/backups/pipelines/${pipelineID}/runs/${runID}/logs`
    );
  }

  getEvents(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    runID: number
  ): Observable<string> {
    return this.http.get<string>(
      `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/backups/pipelines/${pipelineID}/runs/${runID}/events`
    );
  }

  pipelineRunIsFinished(status?: PipelineRunStatus) {
    if (!status) {
      return;
    }
    return !['pending', 'scheduled', 'running'].includes(status);
  }

  pipelineRunIsNotReady(status?: PipelineRunStatus) {
    if (!status) {
      return;
    }
    return ['pending', 'scheduled'].includes(status);
  }
}

export type PipelineRun = {
  status: PipelineRunStatus;
  triggerer: User;
  id: number;
  trigger_time: string;
  environment: PipelineRunEnvironment;
};

interface PipelineRunEnvironment {
  [key: string]: string;
}

export type PipelineRunStatus =
  | 'pending'
  | 'scheduled'
  | 'running'
  | 'success'
  | 'timeout'
  | 'failure'
  | 'unknown';
