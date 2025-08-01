/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconButton } from '@angular/material/button';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogRef,
} from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { Observable, map } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Project, ToolModel } from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-move-model',
  templateUrl: './move-model.component.html',
  imports: [
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatIcon,
    MatSuffix,
    MatIconButton,
    AsyncPipe,
  ],
})
export class MoveModelComponent {
  private modelService = inject(ModelWrapperService);
  private dialogRef = inject<MatDialogRef<MoveModelComponent>>(MatDialogRef);
  private toastService = inject(ToastService);
  projectService = inject(ProjectWrapperService);
  private dialog = inject(MatDialog);
  data = inject<{
    projectSlug: string;
    model: ToolModel;
  }>(MAT_DIALOG_DATA);

  selectedProject?: Project;
  search = '';
  filteredProjects$: Observable<Project[] | undefined>;
  constructor() {
    const projectService = this.projectService;
    const data = this.data;

    this.projectService.loadProjects('manager');
    this.filteredProjects$ = projectService.projects$.pipe(
      map((projects) =>
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
              `The model “${this.data.model.name}” was successfully moved to project "${project.slug}".`,
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
      map((projects) =>
        projects?.filter((project) =>
          project.slug.toLowerCase().includes(this.search.toLowerCase()),
        ),
      ),
    );
  }
}
