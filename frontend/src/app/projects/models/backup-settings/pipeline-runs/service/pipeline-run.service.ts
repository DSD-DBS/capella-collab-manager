/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { User } from 'src/app/services/user/user.service';

@Injectable({
  providedIn: 'root',
})
@UntilDestroy()
export class PipelineRunService {
  constructor(
    private http: HttpClient,
    private pipelineService: PipelineService,
    private breadcrumbsService: BreadcrumbsService
  ) {
    this.resetPipelineRunsOnPipelineChange();
  }

  _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(undefined);
  pipelineRun = this._pipelineRun.asObservable();

  _pipelineRuns = new BehaviorSubject<PipelineRun[] | undefined>(undefined);
  pipelineRuns = this._pipelineRuns.asObservable();

  urlFactory(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number
  ): string {
    return `${this.pipelineService.urlFactory(
      projectSlug,
      modelSlug
    )}/${pipelineID}/runs`;
  }

  resetPipelineRun() {
    this._pipelineRun.next(undefined);
  }

  resetPipelineRunsOnPipelineChange() {
    this.pipelineService.pipeline.subscribe(() => {
      this.resetPipelineRuns();
    });
  }

  resetPipelineRuns() {
    this._pipelineRuns.next(undefined);
  }

  triggerRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    includeCommitHistory: boolean
  ): Observable<PipelineRun> {
    return this.http.post<PipelineRun>(
      this.urlFactory(projectSlug, modelSlug, pipelineID),
      { include_commit_history: includeCommitHistory }
    );
  }

  loadPipelineRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number
  ): Observable<PipelineRun> {
    return this.http
      .get<PipelineRun>(
        `${this.urlFactory(
          projectSlug,
          modelSlug,
          pipelineID
        )}/${pipelineRunID}`
      )
      .pipe(
        tap((pipelineRun) => {
          this._pipelineRun.next(pipelineRun);
          this.breadcrumbsService.updatePlaceholder({ pipelineRun });
        })
      );
  }

  loadPipelineRuns(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number
  ): Observable<PipelineRun[]> {
    return this.http
      .get<PipelineRun[]>(this.urlFactory(projectSlug, modelSlug, pipelineID))
      .pipe(
        tap((pipelineRuns) => {
          this._pipelineRuns.next(pipelineRuns);
        })
      );
  }

  getLogs(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number
  ): Observable<string> {
    return this.http.get<string>(
      `${this.urlFactory(
        projectSlug,
        modelSlug,
        pipelineID
      )}/${pipelineRunID}/logs`
    );
  }

  getEvents(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number
  ): Observable<string> {
    return this.http.get<string>(
      `${this.urlFactory(
        projectSlug,
        modelSlug,
        pipelineID
      )}/${pipelineRunID}/events`
    );
  }

  pipelineRunIsFinished(status: PipelineRunStatus) {
    return !['pending', 'scheduled', 'running'].includes(status);
  }

  pipelineRunIsNotReady(status: PipelineRunStatus) {
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
