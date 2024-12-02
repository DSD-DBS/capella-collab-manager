/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton, MatAnchor } from '@angular/material/button';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { MatStepper, MatStep, MatStepLabel } from '@angular/material/stepper';
import { RouterLink } from '@angular/router';
import { ProjectType, ProjectVisibility } from 'src/app/openapi';
import {
  CreateModelComponent,
  CreateModelStep,
} from 'src/app/projects/models/create-model/create-model.component';
import { ToastService } from '../../helpers/toast/toast.service';
import { CreateModelComponent as CreateModelComponent_1 } from '../models/create-model/create-model.component';
import { ProjectUserSettingsComponent } from '../project-detail/project-users/project-user-settings.component';
import { ProjectUserService } from '../project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from '../service/project.service';

@Component({
  selector: 'app-create-project',
  templateUrl: './create-project.component.html',
  imports: [
    MatStepper,
    MatStep,
    MatStepLabel,
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatRadioGroup,
    MatRadioButton,
    MatButton,
    MatIcon,
    ProjectUserSettingsComponent,
    MatAnchor,
    CreateModelComponent_1,
    RouterLink,
    AsyncPipe,
  ],
})
export class CreateProjectComponent implements OnInit, OnDestroy {
  @ViewChild('model_creator') model_creator!: CreateModelComponent;

  public modelCreationStep: CreateModelStep = 'create-model';

  constructor(
    public projectService: ProjectWrapperService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
  ) {}

  form = new FormGroup({
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.projectService.asyncSlugValidator(),
    }),
    description: new FormControl(''),
    visibility: new FormControl('private'),
    type: new FormControl('general'),
  });

  ngOnInit(): void {
    this.projectService.loadProjects();
  }

  ngOnDestroy(): void {
    this.projectService.clearProject();
  }

  createProject(stepper: MatStepper): void {
    if (this.form.valid) {
      this.projectService
        .createProject({
          name: this.form.value.name!,
          description: this.form.value.description!,
          visibility: this.form.value.visibility! as ProjectVisibility,
          type: this.form.value.type! as ProjectType,
        })
        .subscribe((project) => {
          this.toastService.showSuccess(
            `The project “${project.name}” was successfully created.`,
            'Project created',
          );
          stepper.steps.get(0)!.completed = true;
          stepper.next();
          stepper.steps.get(0)!.editable = false;
        });
    }
  }

  getColorByModelCreationStep(): string {
    switch (this.modelCreationStep) {
      case 'complete':
        return 'primary';
      default:
        return 'warn';
    }
  }
}
