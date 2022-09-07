/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {
  Connectable,
  connectable,
  map,
  Subject,
  Subscription,
  switchMap,
} from 'rxjs';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-wrapper',
  templateUrl: './project-wrapper.component.html',
  styleUrls: ['./project-wrapper.component.css'],
})
export class ProjectWrapperComponent implements OnInit, OnDestroy {
  param_subject?: Connectable<string>;
  project_subscription?: Subscription;
  models_subscription?: Subscription;

  constructor(
    private _route: ActivatedRoute,
    public projectService: ProjectService,
    public _modelService: ModelService
  ) {}

  ngOnInit(): void {
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
      .subscribe(this.projectService._project);

    this.models_subscription = param_subject
      .pipe(switchMap(this._modelService.list.bind(this._modelService)))
      .subscribe(this._modelService._models);

    param_subject.connect();
  }

  ngOnDestroy(): void {
    this.project_subscription?.unsubscribe();
    this.models_subscription?.unsubscribe();
    this.projectService._project.next(undefined);
    this._modelService._models.next(undefined);
  }
}
