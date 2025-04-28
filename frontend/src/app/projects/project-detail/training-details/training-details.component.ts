/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { MatAnchor, MatMiniFabAnchor } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { MarkdownComponent, provideMarkdown } from 'ngx-markdown';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { combineLatest } from 'rxjs';
import { SKIP_ERROR_HANDLING_CONTEXT } from 'src/app/general/error-handling/error-handling.interceptor';
import {
  GitModel,
  ProjectsModelsREADMEService,
  ToolModel,
} from 'src/app/openapi';
import {
  getPrimaryGitModel,
  ModelWrapperService,
} from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-training-details',
  imports: [
    CommonModule,
    MatAnchor,
    RouterLink,
    MatTooltip,
    MatIcon,
    NgxSkeletonLoaderModule,
    MatMiniFabAnchor,
    AsyncPipe,
    MarkdownComponent,
  ],
  templateUrl: './training-details.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  providers: [provideMarkdown()],
})
export class TrainingDetailsComponent implements OnInit {
  modelService = inject(ModelWrapperService);
  projectUserService = inject(ProjectUserService);
  projectService = inject(ProjectWrapperService);
  private readmeService = inject(ProjectsModelsREADMEService);

  getPrimaryGitModelURL(model: ToolModel): string {
    const primaryModel = getPrimaryGitModel(model);
    return primaryModel ? primaryModel.path : '';
  }

  getPrimaryGitModel(model: ToolModel): GitModel | undefined {
    return getPrimaryGitModel(model);
  }

  readmes = new Map<string, Readme>();

  ngOnInit(): void {
    combineLatest([this.projectService.project$, this.modelService.models$])
      .pipe(untilDestroyed(this))
      .subscribe(([project, models]) => {
        if (!models || !project) return;
        if (project.type === 'general') return;
        for (const model of models) {
          this.readmeService
            .getReadme(project.slug, model.slug, 'body', false, {
              httpHeaderAccept: 'text/markdown',
              context: SKIP_ERROR_HANDLING_CONTEXT,
            })
            .subscribe({
              next: (readme) => {
                this.readmes.set(model.slug, { readme });
              },
              error: (error) => {
                error = JSON.parse(error.error);
                this.readmes.set(model.slug, {
                  errorMessage: error?.detail.reason,
                  errorCode: error?.detail?.err_code,
                });
              },
            });
        }
      });
  }
}

interface Readme {
  errorMessage?: string;
  errorCode?: string;
  readme?: string;
}
