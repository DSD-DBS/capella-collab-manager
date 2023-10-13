/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { HistoryEvent } from 'src/app/events/service/events.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { Page, PageWrapper } from 'src/app/schemes';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectAuditLogService {
  private _projectHistoryEventPages = new BehaviorSubject<
    PageWrapper<HistoryEvent>
  >({
    pages: [],
    total: undefined,
  });

  public readonly projectHistoryEventsPages$ =
    this._projectHistoryEventPages.asObservable();

  constructor(
    private http: HttpClient,
    private projectService: ProjectService,
  ) {
    this.resetProjectAuditLogOnPipelineChange();
  }

  resetProjectAuditLogOnPipelineChange() {
    this.projectService.project$.subscribe(() => {
      this.resetProjectHistoryEvents();
    });
  }

  getProjectHistoryEventPage(
    pageNumber: number,
  ): Observable<Page<HistoryEvent> | undefined | 'loading'> {
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

    this.http
      .get<Page<HistoryEvent>>(
        `${environment.backend_url}/projects/${projectSlug}/events?page=${page}&size=${size}`,
      )
      .subscribe((projectEvents) => {
        const projectHistoryEventPages =
          this._projectHistoryEventPages.getValue();
        projectHistoryEventPages.pages[page - 1] = projectEvents;

        this.initalizeProjectHistoryEventWrapper(projectHistoryEventPages);

        this._projectHistoryEventPages.next(projectHistoryEventPages);
      });
  }

  resetProjectHistoryEvents(): void {
    this._projectHistoryEventPages.next({
      pages: [],
      total: undefined,
    });
  }

  private initalizeProjectHistoryEventWrapper(
    pageWrapper: PageWrapper<HistoryEvent>,
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
      { length: firstPage.pages },
      (_, i) => pageWrapper.pages[i],
    );
  }
}
