/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, NgFor } from '@angular/common';
import { Component, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import {
  MatFormField,
  MatLabel,
  MatError,
  MatHint,
} from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { MatTooltip } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import slugify from 'slugify';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { PatchProject, Project } from 'src/app/openapi';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-project-metadata',
  templateUrl: './edit-project-metadata.component.html',
  styleUrls: ['./edit-project-metadata.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    NgIf,
    MatError,
    MatHint,
    MatRadioGroup,
    NgFor,
    MatRadioButton,
    MatTooltip,
    MatButton,
  ],
})
export class EditProjectMetadataComponent implements OnInit, OnChanges {
  canDelete = false;
  project?: Project;

  constructor(
    public projectService: ProjectWrapperService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private router: Router,
  ) {}

  form = new FormGroup({
    name: new FormControl<string>('', Validators.required),
    description: new FormControl<string>(''),
    visibility: new FormControl(''),
    type: new FormControl(''),
  });

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => {
        this.project = project;
        this.form.controls.name.setAsyncValidators(
          this.projectService.asyncSlugValidator(project),
        );
        this.form.patchValue(project);
      });
  }

  ngOnChanges(_changes: SimpleChanges): void {
    if (this.project) {
      this.projectService.loadProjectBySlug(this.project.slug);
    }
  }

  updateProject() {
    if (this.form.valid && this.project) {
      this.projectService
        .updateProject(this.project.slug, this.form.value as PatchProject)
        .subscribe((project) => {
          this.router.navigateByUrl(`/project/${project.slug}`);
          this.toastService.showSuccess(
            'Project updated',
            `The new name is: '${project.name}' and the new description is '${
              project.description || ''
            }'`,
          );
        });
    }
  }

  get newSlug(): string | null {
    return this.form.value.name
      ? slugify(this.form.value.name, { lower: true })
      : null;
  }
}
