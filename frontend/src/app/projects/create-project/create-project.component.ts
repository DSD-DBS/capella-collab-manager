// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnDestroy, OnInit } from '@angular/core';
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
import { ToastrService } from 'ngx-toastr';
import { connectable, filter, Subject, switchMap, tap } from 'rxjs';
import slugify from 'slugify';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-create-project',
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.css'],
})
export class CreateProjectComponent implements OnInit, OnDestroy {
  createProjectForm = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
  });

  private project_details = false;

  constructor(
    public projectService: ProjectService,
    private router: Router,
    private toastrService: ToastrService,
    private navBarService: NavBarService
  ) {
    this.navBarService.title = 'Create Project';
  }

  slugValidator(slugs: string[]): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      let new_slug = slugify(control.value, { lower: true });
      for (let slug of slugs) {
        if (slug == new_slug) {
          return { uniqueSlug: { value: slug } };
        }
      }
      return null;
    };
  }

  ngOnInit(): void {
    this.projectService._projects
      .pipe(filter(Boolean))
      .subscribe((projects) => {
        this.createProjectForm.controls.name.addValidators(
          this.slugValidator(projects.map((p) => p.slug))
        );
      });
  }

  ngOnDestroy(): void {
    if (!this.project_details) {
      this.projectService._project.next(undefined);
    }
  }

  createProject(stepper: MatStepper): void {
    if (this.createProjectForm.valid) {
      const project_creation_subject = connectable<Project>(
        this.projectService.createProject(this.createProjectForm.value),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      project_creation_subject
        .pipe(tap(this.projectService._project))
        .subscribe((project) => {
          this.toastrService.success(
            `The project “${project!.name}” was successfuly created.`,
            'Project created'
          );
          stepper.steps.get(0)!.completed = true;
          stepper.next();
          stepper.steps.get(0)!.editable = false;
        });

      project_creation_subject
        .pipe(switchMap(() => this.projectService.list()))
        .subscribe(this.projectService._projects);

      project_creation_subject.connect();
    }
  }

  finish(): void {
    this.project_details = true;
    this.router.navigate(['/project', this.projectService.project!.slug]);
  }
}
