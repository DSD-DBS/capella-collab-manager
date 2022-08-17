/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormGroupDirective,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/services/modelsources/t4c-repos/t4c-repo.service';
import { ProjectDeletionDialogComponent } from './project-deletion-dialog/project-deletion-dialog.component';

@Component({
  selector: 'app-t4c-repo-settings',
  templateUrl: './t4c-repo-settings.component.html',
  styleUrls: ['./t4c-repo-settings.component.css'],
})
export class T4CRepoSettingsComponent implements OnInit {
  createProjectForm = new FormGroup({
    name: new FormControl('', Validators.required),
  });

  _repository: string = '';

  @ViewChild('projectsList') projectsList: any;

  @Input()
  set repository(value: string) {
    this._repository = value;
    this.refreshProjects();
  }

  get repository() {
    return this._repository;
  }

  projectNonexistenceValidator(): Validators {
    return (control: AbstractControl): ValidationErrors | null => {
      for (let project of this.projectService.repositories) {
        if (project.name == control.value) {
          return { projectExistsError: true };
        }
      }
      return null;
    };
  }

  constructor(
    public projectService: T4CRepoService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {}

  refreshProjects(): void {
    this.projectService.getRepositoryProjects(this.repository).subscribe();
  }

  createProject(formDirective: FormGroupDirective): void {
    if (this.createProjectForm.valid && this.createProjectForm.value.name) {
      this.projectService
        .createRepositoryProject(
          this.repository,
          this.createProjectForm.value.name
        )
        .subscribe(() => {
          this.refreshProjects();
          formDirective.resetForm();
          this.createProjectForm.reset();
        });
    }
  }

  removeProject(project: T4CRepository): void {
    const dialogRef = this.dialog.open(ProjectDeletionDialogComponent, {
      data: project,
    });

    dialogRef.afterClosed().subscribe((val) => {
      if (val) {
        this.refreshProjects();
      }
    });
  }

  get selectedProject(): T4CRepository {
    return this.projectsList.selectedOptions.selected[0].value;
  }
}
