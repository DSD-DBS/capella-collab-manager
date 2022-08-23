// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

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
import { ToastrService } from 'ngx-toastr';
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
import { CreateModelComponent } from 'src/app/models/create-model/create-model.component';
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
  @ViewChild('model_creator') model_creator!: CreateModelComponent;

  form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
  });

  private project_detail = false;
  private projects_slugs = new BehaviorSubject<string[]>([]);
  private slugs_subscription?: Subscription;
  public _reload = false;

  constructor(
    public projectService: ProjectService,
    private router: Router,
    private toastrService: ToastrService,
    private navBarService: NavBarService
  ) {
    this.navBarService.title = 'Create Project';
  }

  ngOnInit(): void {
    this.form.controls.name.addValidators(this.slugValidator.bind(this));

    let projects = this.projectService._projects;

    this.projectService.list().subscribe({
      next: projects.next.bind(projects),
      error: projects.error.bind(projects),
    });

    this.slugs_subscription = projects
      .pipe(
        filter(Boolean),
        map((projects) => projects.map((p) => p.slug))
      )
      .subscribe(this.projects_slugs);
  }

  ngOnDestroy(): void {
    this.slugs_subscription?.unsubscribe();
    if (!this.project_detail) {
      this.projectService._project.next(undefined);
    }
  }

  createProject(stepper: MatStepper): void {
    let project_subject = this.projectService._project;
    if (this.form.valid) {
      const project_creation_subject = connectable<Project>(
        this.projectService.createProject(this.form.value),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      project_creation_subject
        .pipe(
          tap({
            next: project_subject.next.bind(project_subject),
            error: project_subject.next.bind(project_subject),
          })
        )
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
    this.project_detail = true;
    this.router.navigate(['/project', this.projectService.project!.slug]);
  }

  slugValidator(control: AbstractControl): ValidationErrors | null {
    let new_slug = slugify(control.value, { lower: true });
    for (let slug of this.projects_slugs.value) {
      if (slug == new_slug) {
        return { uniqueSlug: { value: slug } };
      }
    }
    return null;
  }

  onComplete(again?: boolean): void {
    console.log(again);
    if (again) {
      this._reload = true;
      setTimeout(() => {
        this._reload = false;
      });
    } else {
      this.router.navigate(['/project', this.projectService.project!.slug]);
    }
  }
}
