/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

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
  projectSubscription?: Subscription;
  modelsSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {
    const param_subject = connectable<string>(
      this.route.params.pipe(map((params) => params.project)),
      {
        connector: () => new Subject(),
        resetOnDisconnect: false,
      }
    );

    this.projectSubscription = param_subject
      .pipe(
        switchMap(
          this.projectService.getProjectBySlug.bind(this.projectService)
        )
      )
      .subscribe({
        next: this.projectService._project.next.bind(
          this.projectService._project
        ),
        error: (_) => {
          this.projectService._project.next(undefined);
        },
      });

    this.modelsSubscription = param_subject
      .pipe(switchMap(this.modelService.list.bind(this.modelService)))
      .subscribe({
        next: this._modelService._models.next.bind(this.modelService._models),
        error: (_) => {
          this._modelService._models.next(undefined);
        },
      });

    param_subject.connect();
  }

  ngOnDestroy(): void {
    this.projectSubscription?.unsubscribe();
    this.modelsSubscription?.unsubscribe();
    this.projectService._project.next(undefined);
    this.modelService._models.next(undefined);
  }
}
