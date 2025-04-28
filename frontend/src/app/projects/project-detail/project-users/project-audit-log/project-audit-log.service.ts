/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { PageHistoryEvent, ProjectsEventsService } from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Injectable({
  providedIn: 'root',
})
export class ProjectAuditLogService {
  private projectService = inject(ProjectWrapperService);
  private projectEventService = inject(ProjectsEventsService);

  private _projectHistoryEventPages =
    new BehaviorSubject<PageHistoryEventWrapper>({
      pages: [],
      total: undefined,
    });

  public readonly projectHistoryEventsPages$ =
    this._projectHistoryEventPages.asObservable();

  constructor() {
    this.resetProjectAuditLogOnPipelineChange();
  }

  resetProjectAuditLogOnPipelineChange() {
    this.projectService.project$.subscribe(() => {
      this.resetProjectHistoryEvents();
    });
  }

  getProjectHistoryEventPage(
    pageNumber: number,
  ): Observable<PageHistoryEvent | undefined | 'loading'> {
    return this._projectHistoryEventPages.pipe(
      map(
        (projectHistoryEventPages) =>
          projectHistoryEventPages.pages[pageNumber - 1],
      ),
    );
  }

  setProjectEventPageStatusToLoading(page: number) {
    const projectHistoryEventPages = this._projectHistoryEventPages.getValue();
    projectHistoryEventPages.pages[page - 1] = 'loading';
    this._projectHistoryEventPages.next(projectHistoryEventPages);
  }

  loadProjectHistoryEvents(
    projectSlug: string,
    page: number,
    size: number,
  ): void {
    if (
      this._projectHistoryEventPages.getValue().pages[page - 1] !== undefined
    ) {
      // Skip if already loaded or currently loading
      return;
    }

    this.setProjectEventPageStatusToLoading(page);

    this.projectEventService
      .getProjectEvents(projectSlug, page, size)
      .subscribe((projectEvents) => {
        const projectHistoryEventPages =
          this._projectHistoryEventPages.getValue();
        projectHistoryEventPages.pages[page - 1] = projectEvents;

        this.initializeProjectHistoryEventWrapper(projectHistoryEventPages);

        this._projectHistoryEventPages.next(projectHistoryEventPages);
      });
  }

  resetProjectHistoryEvents(): void {
    this._projectHistoryEventPages.next({
      pages: [],
      total: undefined,
    });
  }

  private initializeProjectHistoryEventWrapper(
    pageWrapper: PageHistoryEventWrapper,
  ) {
    if (pageWrapper.total !== undefined) {
      // Do nothing, is already initialized
      return;
    }

    const firstPage = pageWrapper.pages[0];
    if (firstPage === undefined || firstPage === 'loading') {
      throw new TypeError(
        'first page is undefined or loading, but should be of type Page<HistoryEvent>.',
      );
    }

    // Set the correct length for the array
    pageWrapper.pages = Array.from(
      { length: firstPage.pages! },
      (_, i) => pageWrapper.pages[i],
    );
  }
}

export interface PageHistoryEventWrapper {
  pages: (PageHistoryEvent | undefined | 'loading')[];
  total: number | undefined;
}
