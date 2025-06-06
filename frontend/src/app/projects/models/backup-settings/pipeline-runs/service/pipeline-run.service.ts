/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import {
  PagePipelineRun,
  PipelineRun,
  PipelineRunStatus,
  ProjectsModelsBackupsService,
} from 'src/app/openapi';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';

@Injectable({
  providedIn: 'root',
})
@UntilDestroy()
export class PipelineRunWrapperService {
  private pipelineWrapperService = inject(PipelineWrapperService);
  private pipelinesService = inject(ProjectsModelsBackupsService);
  private breadcrumbsService = inject(BreadcrumbsService);

  constructor() {
    this.resetPipelineRunsOnPipelineChange();
  }

  private _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(
    undefined,
  );
  public readonly pipelineRun$ = this._pipelineRun.asObservable();

  private _pipelineRunPages = new BehaviorSubject<PageWrapperPipelineRun>({
    pages: [],
    total: undefined,
  });
  public readonly pipelineRunPages$ = this._pipelineRunPages.asObservable();

  getPipelineRunPage(
    pageNumber: number,
  ): Observable<PagePipelineRun | undefined | 'loading'> {
    return this._pipelineRunPages.pipe(
      map((pipelineRunPages) => pipelineRunPages.pages[pageNumber - 1]),
    );
  }

  resetPipelineRun() {
    this._pipelineRun.next(undefined);
  }

  resetPipelineRunsOnPipelineChange() {
    this.pipelineWrapperService.pipeline$.subscribe(() => {
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

  loadPipelineRun(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
    pipelineRunID: number,
  ): void {
    this.pipelinesService
      .getPipelineRun(projectSlug, pipelineRunID, pipelineID, modelSlug)
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

    this.pipelinesService
      .getPipelineRuns(projectSlug, pipelineID, modelSlug, page, size)
      .subscribe((pipelineRuns) => {
        const pipelineRunPages = this._pipelineRunPages.getValue();
        pipelineRunPages.pages[page - 1] = pipelineRuns;

        this.initalizePipelineRunWrapper(pipelineRunPages);
        this._pipelineRunPages.next(pipelineRunPages);
      });
  }

  private initalizePipelineRunWrapper(pageWrapper: PageWrapperPipelineRun) {
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
      { length: firstPage.pages! },
      (_, i) => pageWrapper.pages[i],
    );
  }

  pipelineRunIsFinished(status: PipelineRunStatus) {
    return !['pending', 'scheduled', 'running'].includes(status);
  }

  pipelineRunIsNotReady(status: PipelineRunStatus) {
    return ['pending', 'scheduled'].includes(status);
  }
}
export interface PageWrapperPipelineRun {
  pages: (PagePipelineRun | undefined | 'loading')[];
  total: number | undefined;
}
