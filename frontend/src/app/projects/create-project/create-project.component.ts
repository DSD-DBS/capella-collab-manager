/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import slugify from 'slugify';
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

  private projectDetails = false;

  public modelCreationStep: CreateModelStep = 'create-model';

  form = new FormGroup({
    name: new FormControl('', [Validators.required, this.slugValidator()]),
    description: new FormControl(''),
  });

  constructor(
    public projectService: ProjectService,
    private router: Router,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.projectService.list().subscribe();
  }

  ngOnDestroy(): void {
    if (!this.projectDetails) {
      this.projectService._project.next(undefined);
    }
  }

  createProject(stepper: MatStepper): void {
    if (this.form.valid) {
      this.projectService
        .createProject(
          {
            name: this.form.value.name!,
            description: this.form.value.description!,
          },
          true
        )
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

  finish(): void {
    this.projectDetails = true;
    this.router.navigate(['/project', this.projectService.project!.slug]);
  }

  slugValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const slug = slugify(control.value, { lower: true });
      if (
        this.projectService.projects
          ?.map((project) => project.slug)
          .includes(slug)
      ) {
        return { uniqueSlug: { value: slug } };
      }
      return null;
    };
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
