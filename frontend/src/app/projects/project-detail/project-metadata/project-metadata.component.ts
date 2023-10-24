/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/general/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import {
  PatchProject,
  Project,
  ProjectService,
} from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent {
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
