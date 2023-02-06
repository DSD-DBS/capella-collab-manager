/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import {
  CreateModelComponent,
  CreateModelStep,
} from 'src/app/projects/models/create-model/create-model.component';
import { ToastService } from '../../helpers/toast/toast.service';
import { ProjectService } from '../service/project.service';

@Component({
  selector: 'app-create-project',
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.css'],
})
export class CreateProjectComponent implements OnInit, OnDestroy {
  @ViewChild('model_creator') model_creator!: CreateModelComponent;

  public modelCreationStep: CreateModelStep = 'create-model';

  constructor(
    public projectService: ProjectService,
    private toastService: ToastService
  ) {}

  form = new FormGroup({
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.projectService.asyncSlugValidator(),
    }),
    description: new FormControl(''),
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
        })
        .subscribe((project) => {
          this.toastService.showSuccess(
            `The project “${project.name}” was successfuly created.`,
            'Project created'
          );
          stepper.steps.get(0)!.completed = true;
          stepper.next();
          stepper.steps.get(0)!.editable = false;
        });
    }
  }

  getColorByModelCreationStep(): string {
    switch (this.modelCreationStep) {
      case 'create-model':
      case 'complete':
        return 'primary';
      default:
        return 'warn';
    }
  }
}
