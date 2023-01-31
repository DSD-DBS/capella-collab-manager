/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { Subject, Subscription, connectable, map, switchMap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectService } from '../service/project.service';

@UntilDestroy({ checkProperties: true })
@Component({
  selector: 'app-project-wrapper',
  templateUrl: './project-wrapper.component.html',
  styleUrls: ['./project-wrapper.component.css'],
})
export class ProjectWrapperComponent implements OnInit, OnDestroy {
  projectSubscription?: Subscription;
  modelsSubscription?: Subscription;
  projectUserSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private projectUserService: ProjectUserService,
    private breadcrumbsService: BreadcrumbsService
  ) {}

  ngOnInit(): void {
    const paramSubject = connectable<string>(
      this.route.params.pipe(map((params) => params.project)),
      {
        connector: () => new Subject(),
        resetOnDisconnect: false,
      }
    );

    this.projectService.project.subscribe((project) =>
      this.breadcrumbsService.updatePlaceholder({ project })
    );

    this.projectSubscription = paramSubject.subscribe((projectSlug) =>
      this.projectService.loadProjectBySlug(projectSlug)
    );

    this.modelsSubscription = paramSubject
      .pipe(
        switchMap((projectSlug: string) =>
          this.modelService.getModels(projectSlug)
        )
      )
      .subscribe({
        next: (models: Model[]) => this.modelService._models.next(models),
        error: () => {
          this.modelService._models.next(undefined);
        },
      });

    this.projectUserSubscription = paramSubject
      .pipe(
        switchMap((projectSlug: string) =>
          this.projectUserService.getOwnProjectUser(projectSlug)
        )
      )
      .subscribe();

    paramSubject.connect();
  }

  ngOnDestroy(): void {
    this.projectService.clearProject();
    this.modelService._models.next(undefined);
    this.projectUserService.projectUser.next(undefined);
    this.breadcrumbsService.updatePlaceholder({ project: undefined });
  }
}
