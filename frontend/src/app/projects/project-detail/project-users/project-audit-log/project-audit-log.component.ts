/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  OnInit,
  QueryList,
  ViewChildren,
  inject,
} from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { UntilDestroy } from '@ngneat/until-destroy';
import { ProjectAuditLogService } from 'src/app/projects/project-detail/project-users/project-audit-log/project-audit-log.service';
import { TextLineSkeletonLoaderComponent } from '../../../../helpers/skeleton-loaders/text-line-skeleton-loader/text-line-skeleton-loader.component';

@Component({
  selector: 'app-project-audit-log',
  templateUrl: './project-audit-log.component.html',
  styleUrls: ['./project-audit-log.component.css'],
  imports: [TextLineSkeletonLoaderComponent, AsyncPipe, DatePipe],
})
@UntilDestroy()
export class ProjectAuditLogComponent implements OnInit, AfterViewInit {
  projectAuditLogService = inject(ProjectAuditLogService);
  private data = inject<{
    projectSlug: string;
  }>(MAT_DIALOG_DATA);

  pageSize = 25;
  pageSizeArray = [...Array(this.pageSize).keys()];

  @ViewChildren('page', { read: ElementRef })
  pageElements?: QueryList<ElementRef>;

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
