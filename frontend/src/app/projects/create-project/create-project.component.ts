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
  Validators,
} from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { ToastService } from '../../helpers/toast/toast.service';
import {
  BehaviorSubject,
  connectable,
  filter,
  map,
  Subject,
  Subscription,
  switchMap,
  tap,
} from 'rxjs';
import slugify from 'slugify';
import {
  CreateModelComponent,
  CreateModelStep,
} from 'src/app/projects/models/create-model/create-model.component';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
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
  @ViewChild('model_creator') model_creator!: CreateModelComponent;

  private projectsSlugs = new BehaviorSubject<string[]>([]);
  private projectDetails = false;
  private slugsSubscription?: Subscription;
  public _reload = false;

  public modelCreationStep: CreateModelStep = 'create-model';

  form = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.slugValidator.bind(this),
    ]),
    description: new FormControl(''),
  });

  constructor(
    public projectService: ProjectService,
    private router: Router,
    private toastService: ToastService,
    private navBarService: NavBarService
  ) {
    this.navBarService.title = 'Create Project';
  }

  ngOnInit(): void {
    let projects = this.projectService._projects;

    this.projectService.list().subscribe({
      next: (value) => {
        projects.next(value);
      },
      error: (_) => {
        projects.next(undefined);
      },
    });

    this.slugsSubscription = projects
      .pipe(
        filter(Boolean),
        map((projects) => projects.map((p) => p.slug))
      )
      .subscribe(this.projectsSlugs);
  }

  ngOnDestroy(): void {
    this.slugsSubscription?.unsubscribe();
    if (!this.projectDetails) {
      this.projectService._project.next(undefined);
    }
  }

  createProject(stepper: MatStepper): void {
    let projectSubject = this.projectService._project;
    if (this.form.valid) {
      const projectConnectable = connectable<Project>(
        this.projectService.createProject({
          name: this.form.value.name!,
          description: this.form.value.name!,
        }),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      projectConnectable
        .pipe(
          tap({
            next: (value) => {
              projectSubject.next(value);
            },
            error: (_) => {
              projectSubject.next(undefined);
            },
          })
        )
        .subscribe((project) => {
          this.toastService.showSuccess(
            `The project “${project!.name}” was successfuly created.`,
            'Project created'
          );
          stepper.steps.get(0)!.completed = true;
          stepper.next();
          stepper.steps.get(0)!.editable = false;
        });

      projectConnectable
        .pipe(switchMap(() => this.projectService.list()))
        .subscribe({
          next: (value) => {
            this.projectService._projects.next(value);
          },
          error: (_) => {
            this.projectService._projects.next(undefined);
          },
        });

      projectConnectable.connect();
    }
  }

  finish(): void {
    this.projectDetails = true;
    this.router.navigate(['/project', this.projectService.project!.slug]);
  }

  slugValidator(control: AbstractControl): ValidationErrors | null {
    let newSlug = slugify(control.value, { lower: true });
    for (let slug of this.projectsSlugs.value) {
      if (slug == newSlug) {
        return { uniqueSlug: { value: slug } };
      }
    }
    return null;
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
