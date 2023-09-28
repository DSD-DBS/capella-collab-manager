/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogRef,
} from '@angular/material/dialog';
import { Observable, map } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/general/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import {
  Project,
  ProjectService,
} from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-move-model',
  templateUrl: './move-model.component.html',
  styleUrls: ['./move-model.component.css'],
})
export class MoveModelComponent {
  selectedProject?: Project;
  search = '';
  filteredProjects$: Observable<Project[] | undefined>;
  constructor(
    private modelService: ModelService,
    private dialogRef: MatDialogRef<MoveModelComponent>,
    private toastService: ToastService,
    public projectService: ProjectService,
    private dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; model: Model },
  ) {
    this.projectService.loadProjectsForRole('manager');
    this.filteredProjects$ = projectService.projects$.pipe(
      map(
        (projects) =>
          projects?.filter((project) => project.slug !== data.projectSlug),
      ),
    );
  }

  onProjectSelect(project: Project) {
    this.selectedProject = project;
  }

  async moveModelToProject(project: Project) {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Move Model',
        text: `Do you really want to move the model ${this.data.model.slug} to the project ${project.slug}?`,
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.modelService
          .updateModel(this.data.projectSlug, this.data.model.slug, {
            description: '',
            nature_id: undefined,
            version_id: undefined,
            project_slug: project.slug,
          })
          .subscribe(() => {
            this.toastService.showSuccess(
              'Model moved',
              `The model “${this.data.model.name}” was successfuly moved to project "${project.slug}".`,
            );
            this.dialogRef.close();
          });
      }
    });
  }

  searchAndFilteredProjects(): Observable<Project[] | undefined> {
    if (!this.search) {
      return this.filteredProjects$;
    }
    return this.filteredProjects$.pipe(
      map(
        (projects) =>
          projects?.filter((project) =>
            project.slug.toLowerCase().includes(this.search.toLowerCase()),
          ),
      ),
    );
  }
}
