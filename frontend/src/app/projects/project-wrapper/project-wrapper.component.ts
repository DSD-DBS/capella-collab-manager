/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { Subscription, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
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
    this.route.params
      .pipe(map((params) => params.project))
      .subscribe((projectSlug: string) => {
        this.projectService.loadProjectBySlug(projectSlug);
        this.modelService.loadModels(projectSlug);
        this.projectUserService.getOwnProjectUser(projectSlug).subscribe();
      });

    this.projectService.project.subscribe((project) =>
      this.breadcrumbsService.updatePlaceholder({ project })
    );
  }

  ngOnDestroy(): void {
    this.projectService.clearProject();
    this.modelService.clearModel();
    this.modelService.clearModels();
    this.projectUserService.projectUser.next(undefined);
    this.breadcrumbsService.updatePlaceholder({ project: undefined });
  }
}
