/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  inject,
} from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, map, switchMap } from 'rxjs';
import { DOCS_URL } from 'src/app/environment';
import { SKIP_ERROR_HANDLING_CONTEXT } from 'src/app/general/error-handling/error-handling.interceptor';
import { ProjectsModelsModelComplexityBadgeService } from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-model-complexity-badge',
  imports: [
    CommonModule,
    MatIconModule,
    NgxSkeletonLoaderModule,
    MatSlideToggleModule,
  ],
  templateUrl: './model-complexity-badge.component.html',
})
@UntilDestroy()
export class ModelComplexityBadgeComponent implements OnChanges {
  private modelComplexityBadgeService = inject(
    ProjectsModelsModelComplexityBadgeService,
  );
  private projectService = inject(ProjectWrapperService);

  @Input() modelSlug?: string;

  complexityBadge?: string | ArrayBuffer | null;
  loadingComplexityBadge = true;

  errorMessage?: string;
  errorCode?: string;

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
            undefined,
            undefined,
            {
              context: SKIP_ERROR_HANDLING_CONTEXT,
            },
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
          this.errorMessage = err.error?.detail.reason;
          this.errorCode = err.error?.detail?.err_code;
        },
      });
  }

  openModelComplexityBadgeDocs() {
    window.open(DOCS_URL + '/user/projects/models/complexity_badge/', '_blank');
  }
}
