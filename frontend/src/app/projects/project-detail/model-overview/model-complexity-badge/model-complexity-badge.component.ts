/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, map, switchMap } from 'rxjs';
import { ErrorHandlingInterceptor } from 'src/app/general/error-handling/error-handling.interceptor';
import { ModelComplexityBadgeService } from 'src/app/projects/project-detail/model-overview/model-complexity-badge/service/model-complexity-badge.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { environment } from 'src/environments/environment';
@Component({
  selector: 'app-model-complexity-badge',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    NgxSkeletonLoaderModule,
    MatSlideToggleModule,
  ],
  templateUrl: './model-complexity-badge.component.html',
  styleUrls: ['./model-complexity-badge.component.css'],
})
@UntilDestroy()
export class ModelComplexityBadgeComponent implements OnChanges {
  @Input() modelSlug?: string;

  complexityBadge?: string | ArrayBuffer | null;
  loadingComplexityBadge = true;

  errorMessage?: string;
  errorCode?: string;

  constructor(
    private modelComplexityBadgeService: ModelComplexityBadgeService,
    private projectService: ProjectService,
  ) {}

  ngOnChanges(_: SimpleChanges) {
    if (this.modelSlug) {
      this.loadModelComplexityBadge();
    }
  }

  loadModelComplexityBadge() {
    this.projectService.project$
      .pipe(
        untilDestroyed(this),
        filter(Boolean),
        map((project) => project.slug),
        switchMap((projectSlug: string) => {
          return this.modelComplexityBadgeService.getModelComplexityBadge(
            projectSlug,
            this.modelSlug!,
          );
        }),
      )
      .subscribe({
        next: (response: Blob) => {
          this.loadingComplexityBadge = false;
          const reader = new FileReader();
          reader.readAsDataURL(response);
          reader.onloadend = () => {
            this.complexityBadge = reader.result;
          };
        },
        error: (err) => {
          this.loadingComplexityBadge = false;
          this.errorMessage = ErrorHandlingInterceptor.getErrorReason(
            err.error?.detail,
          );
          this.errorCode = err.error?.detail?.err_code;
        },
      });
  }

  openModelComplexityBadgeDocs() {
    let docsURL = '/docs';
    if ('docsURL' in environment) {
      docsURL = environment.docs_url as string;
    }
    window.open(docsURL + '/user/projects/models/complexity_badge/', '_blank');
  }
}
