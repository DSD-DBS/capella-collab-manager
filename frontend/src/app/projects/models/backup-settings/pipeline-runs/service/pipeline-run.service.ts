/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { User } from 'src/app/openapi';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { Page, PageWrapper } from 'src/app/schemes';

@Injectable({
  providedIn: 'root',
})
@UntilDestroy()
export class PipelineRunService {
  constructor(
    private http: HttpClient,
    private pipelineService: PipelineService,
    private breadcrumbsService: BreadcrumbsService,
  ) {
    this.resetPipelineRunsOnPipelineChange();
  }

  private _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(
    undefined,
  );
  public readonly pipelineRun$ = this._pipelineRun.asObservable();

  private _pipelineRunPages = new BehaviorSubject<PageWrapper<PipelineRun>>({
    pages: [],
    total: undefined,
  });
  public readonly pipelineRunPages$ = this._pipelineRunPages.asObservable();

  getPipelineRunPage(
    pageNumber: number,
  ): Observable<Page<PipelineRun> | undefined | 'loading'> {
    return this._pipelineRunPages.pipe(
      map((pipelineRunPages) => pipelineRunPages.pages[pageNumber - 1]),
    );
  }

  urlFactory(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
  ): string {
    return `${this.pipelineService.urlFactory(
      projectSlug,
      modelSlug,
    )}/${pipelineID}/runs`;
  }

  resetPipelineRun() {
    this._pipelineRun.next(undefined);
  }

  resetPipelineRunsOnPipelineChange() {
    this.pipelineService.pipeline$.subscribe(() => {
      this.resetPipelineRuns();
    });
  }

  resetPipelineRuns() {
    this._pipelineRunPages.next({
      pages: [],
      total: undefined,
    });
  }

  setPipelineRunPageStatusToLoading(page: number) {
    const pipelineRunPages = this._pipelineRunPages.getValue();
    pipelineRunPages.pages[page - 1] = 'loading';
    this._pipelineRunPages.next(pipelineRunPages);
  }

  triggerRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    includeCommitHistory: boolean,
  ): Observable<PipelineRun> {
    return this.http.post<PipelineRun>(
      this.urlFactory(projectSlug, modelSlug, pipelineID),
      { include_commit_history: includeCommitHistory },
    );
  }

  loadPipelineRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number,
  ): void {
    this.http
      .get<PipelineRun>(
        `${this.urlFactory(
          projectSlug,
          modelSlug,
          pipelineID,
        )}/${pipelineRunID}`,
      )
      .subscribe((pipelineRun) => {
        this._pipelineRun.next(pipelineRun);
        this.breadcrumbsService.updatePlaceholder({ pipelineRun });
      });
  }

  loadPipelineRuns(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    page: number,
    size: number,
  ): void {
    if (this._pipelineRunPages.getValue().pages[page - 1] !== undefined) {
      // Skip if already loaded or currently loading
      return;
    }

    this.setPipelineRunPageStatusToLoading(page);

    this.http
      .get<
        Page<PipelineRun>
      >(`${this.urlFactory(projectSlug, modelSlug, pipelineID)}?page=${page}&size=${size}`)
      .subscribe((pipelineRuns) => {
        const pipelineRunPages = this._pipelineRunPages.getValue();
        pipelineRunPages.pages[page - 1] = pipelineRuns;

        this.initalizePipelineRunWrapper(pipelineRunPages);

        this._pipelineRunPages.next(pipelineRunPages);
      });
  }

  private initalizePipelineRunWrapper(pageWrapper: PageWrapper<PipelineRun>) {
    if (pageWrapper.total !== undefined) {
      // Do nothing, is already initialized
      return;
    }

    const firstPage = pageWrapper.pages[0];
    if (firstPage === undefined || firstPage === 'loading') {
      throw new TypeError(
        'first page is undefined or loading, but should be of type Page<PipelineRun>.',
      );
    }

    // Set the correct length for the array
    pageWrapper.pages = Array.from(
      { length: firstPage.pages },
      (_, i) => pageWrapper.pages[i],
    );
  }

  getLogs(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number,
  ): Observable<string> {
    return this.http.get<string>(
      `${this.urlFactory(
        projectSlug,
        modelSlug,
        pipelineID,
      )}/${pipelineRunID}/logs`,
    );
  }

  getEvents(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number,
  ): Observable<string> {
    return this.http.get<string>(
      `${this.urlFactory(
        projectSlug,
        modelSlug,
        pipelineID,
      )}/${pipelineRunID}/events`,
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
