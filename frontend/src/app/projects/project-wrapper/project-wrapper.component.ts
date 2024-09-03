/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from '../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-wrapper',
  templateUrl: './project-wrapper.component.html',
  styleUrls: ['./project-wrapper.component.css'],
  standalone: true,
  imports: [RouterOutlet],
})
export class ProjectWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(
        map((params) => params.project),
        untilDestroyed(this),
      )
      .subscribe((projectSlug: string) => {
        this.projectService.loadProjectBySlug(projectSlug);
        this.modelService.loadModels(projectSlug);
      });

    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) =>
        this.breadcrumbsService.updatePlaceholder({ project }),
      );
  }

  ngOnDestroy(): void {
    this.projectService.clearProject();
    this.modelService.clearModel();
    this.modelService.clearModels();
    this.breadcrumbsService.updatePlaceholder({
      project: undefined,
    });
  }
}
