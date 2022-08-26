// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {
  BehaviorSubject,
  Connectable,
  connectable,
  map,
  Subject,
  Subscription,
  switchMap,
  tap,
} from 'rxjs';
import { ModelService } from 'src/app/services/model/model.service';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-wrapper',
  templateUrl: './project-wrapper.component.html',
  styleUrls: ['./project-wrapper.component.css'],
})
export class ProjectWrapperComponent implements OnInit, OnDestroy {
  param_subject?: Connectable<string>;
  project_subscription?: Subscription;
  models_subscription?: Subscription;
  is_error?: Boolean;

  constructor(
    private _route: ActivatedRoute,
    public projectService: ProjectService,
    public modelServico: ModelService
  ) {}

  ngOnInit(): void {
    const project = this.projectService._project;
    const models = this.modelServico._models;
    const param_subject = connectable<string>(
      this._route.params.pipe(map((params) => params.project)),
      {
        connector: () => new Subject(),
        resetOnDisconnect: false,
      }
    );

    this.project_subscription = param_subject
      .pipe(
        switchMap(
          this.projectService.getProjectBySlug.bind(this.projectService)
        )
      )
      .subscribe({
        next: project.next.bind(project),
        error: (_) => {
          project.next(undefined);
          this.is_error = true;
        },
      });

    this.models_subscription = param_subject
      .pipe(switchMap(this.modelServico.list.bind(this.modelServico)))
      .subscribe({
        next: models.next.bind(models),
        error: (_) => {
          models.next(undefined);
        },
      });

    param_subject.connect();
  }

  ngOnDestroy(): void {
    this.project_subscription?.unsubscribe();
    this.models_subscription?.unsubscribe();
    this.projectService._project.next(undefined);
    this.modelServico._models.next(undefined);
  }
}
