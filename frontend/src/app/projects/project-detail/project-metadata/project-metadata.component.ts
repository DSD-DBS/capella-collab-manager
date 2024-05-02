/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Project } from 'src/app/openapi';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { PatchProject, ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-metadata',
  standalone: true,
  imports: [
    MatIconModule,
    NgxSkeletonLoaderModule,
    MatButtonModule,
    MatTooltipModule,
    RouterLink,
  ],
  templateUrl: './project-metadata.component.html',
})
export class ProjectMetadataComponent implements OnInit {
  project?: Project;
  canDelete = false;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => (this.project = project));

    this.modelService.models$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => (this.canDelete = !models.length));
  }

  deleteProject(): void {
    if (!(this.canDelete && this.project)) {
      return;
    }

    const projectSlug = this.project.slug;

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete Project',
        text: 'Do you really want to delete this project? All assigned users will lose access to it! The project cannot be restored!',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.projectService.deleteProject(projectSlug).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Project deleted',
              `${projectSlug} has been deleted`,
            );
            this.router.navigate(['../../projects'], {
              relativeTo: this.route,
            });
          },
        });
      }
    });
  }

  toggleArchive(): void {
    if (this.project) {
      const projectSlug = this.project.slug;

      if (!this.project.is_archived) {
        const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
          data: {
            title: 'Archive Project',
            text: 'Do you really want to archive the project? All pipelines of the existing project models wil be deleted.',
            requiredInput: projectSlug,
          },
        });

        dialogRef.afterClosed().subscribe((result: boolean) => {
          if (result) {
            this.updateProjectArchivalStatus(projectSlug, true);
          }
        });
      } else {
        this.updateProjectArchivalStatus(projectSlug, false);
      }
    }
  }

  updateProjectArchivalStatus(projectSlug: string, is_archived: boolean) {
    this.projectService
      .updateProject(projectSlug, { is_archived: is_archived } as PatchProject)
      .subscribe((project) =>
        this.toastService.showSuccess(
          'Project updated',
          `The project ${project.slug} is now ${
            is_archived ? 'archived' : 'unarchived'
          }`,
        ),
      );
  }
}
