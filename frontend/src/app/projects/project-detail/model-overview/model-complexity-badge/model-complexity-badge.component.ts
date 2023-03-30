/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map, switchMap } from 'rxjs';
import { ModelComplexityBadgeService } from 'src/app/projects/project-detail/model-overview/model-complexity-badge/service/model-complexity-badge.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-model-complexity-badge',
  templateUrl: './model-complexity-badge.component.html',
  styleUrls: ['./model-complexity-badge.component.css'],
})
@UntilDestroy()
export class ModelComplexityBadgeComponent implements OnChanges {
  @Input() modelSlug?: string;

  complexityBadge?: string | ArrayBuffer | null;
  loadingComplexityBadge: boolean = true;

  ngOnChanges(_: SimpleChanges) {
    if (this.modelSlug) {
      this.loadModelComplexityBadge();
    }
  }

  loadModelComplexityBadge() {
    this.projectService.project
      .pipe(
        untilDestroyed(this),
        filter(Boolean),
        map((project) => project.slug),
        switchMap((projectSlug: string) => {
          return this.modelComplexityBadgeService.getModelComplexityBadge(
            projectSlug,
            this.modelSlug!
          );
        })
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
        error: () => {
          this.loadingComplexityBadge = false;
        },
      });
  }

  constructor(
    private modelComplexityBadgeService: ModelComplexityBadgeService,
    private projectService: ProjectService
  ) {}
}
