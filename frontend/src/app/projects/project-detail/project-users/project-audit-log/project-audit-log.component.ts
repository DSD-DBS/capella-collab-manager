/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  ElementRef,
  Inject,
  QueryList,
  ViewChildren,
} from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { UntilDestroy } from '@ngneat/until-destroy';
import { ProjectAuditLogService } from 'src/app/projects/project-detail/project-users/project-audit-log/service/project-audit-log.service';

@Component({
  selector: 'app-project-audit-log',
  templateUrl: './project-audit-log.component.html',
  styleUrls: ['./project-audit-log.component.css'],
})
@UntilDestroy()
export class ProjectAuditLogComponent {
  pageSize = 25;
  pageSizeArray = [...Array(this.pageSize).keys()];

  @ViewChildren('page', { read: ElementRef })
  pageElements?: QueryList<ElementRef>;

  constructor(
    public projectAuditLogService: ProjectAuditLogService,
    @Inject(MAT_DIALOG_DATA)
    private data: { projectSlug: string },
  ) {}

  ngOnInit() {
    this.projectAuditLogService.loadProjectHistoryEvents(
      this.data.projectSlug,
      1,
      this.pageSize,
    );
  }

  ngAfterViewInit(): void {
    this.observeVisibleEvents(this.data.projectSlug);
  }

  observeVisibleEvents(projectSlug: string) {
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[], _: IntersectionObserver) => {
        entries
          .filter((entry) => entry.isIntersecting) // Only visible elements
          .filter((entry) => entry.target.id !== '1') // Initial page is pre-loaded in ngOnInit
          .forEach((entry) => {
            this.projectAuditLogService.loadProjectHistoryEvents(
              projectSlug,
              parseInt(entry.target.id),
              this.pageSize,
            );
          });
      },
      {
        root: null,
        threshold: 0.1,
      },
    );

    this.pageElements?.changes.subscribe((res) => {
      res.forEach((pageElement: ElementRef) => {
        observer.observe(pageElement.nativeElement);
      });
    });
  }
}
