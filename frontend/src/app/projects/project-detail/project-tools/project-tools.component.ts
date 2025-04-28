/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, switchMap, take, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ProjectsToolsService, ProjectTool } from 'src/app/openapi';
import { ProjectToolsWrapperService } from 'src/app/projects/project-detail/project-tools/project-tools-wrapper.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-tools',
  imports: [
    CommonModule,
    RouterLink,
    MatTooltipModule,
    MatButtonModule,
    MatIconModule,
    NgxSkeletonLoaderModule,
  ],
  templateUrl: './project-tools.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
})
export class ProjectToolsComponent {
  projectUserService = inject(ProjectUserService);
  projectWrapperService = inject(ProjectWrapperService);
  projectToolsWrapperService = inject(ProjectToolsWrapperService);
  private projectToolService = inject(ProjectsToolsService);
  private toastService = inject(ToastService);

  unlinkTool(tool: ProjectTool): void {
    const tool_id = tool.id;
    if (!tool_id) return;

    this.projectWrapperService.project$
      .pipe(
        filter(Boolean),
        take(1),
        switchMap((project) =>
          this.projectToolService.deleteToolFromProject(project.slug, tool_id),
        ),
        tap(() => {
          this.projectToolsWrapperService.loadProjectTools();
          this.toastService.showSuccess(
            'Tool unlinked from project',
            `The tool ${tool.tool.name} ${tool.tool_version.name} was successfully unlinked from the project.`,
          );
        }),
      )
      .subscribe();
  }
}
