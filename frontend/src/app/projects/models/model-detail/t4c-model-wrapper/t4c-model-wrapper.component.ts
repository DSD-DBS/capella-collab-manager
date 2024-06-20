/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-t4c-model-wrapper',
  templateUrl: './t4c-model-wrapper.component.html',
  styleUrls: ['./t4c-model-wrapper.component.css'],
  standalone: true,
  imports: [RouterOutlet],
})
export class T4CModelWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    private t4cModelService: T4CModelService,
    private breadCrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.route.params.pipe(map((params) => parseInt(params.t4c_model_id))),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model, t4cModelId]) =>
        this.t4cModelService.loadT4CModel(project.slug, model.slug, t4cModelId),
      );

    this.t4cModelService.t4cModel$
      .pipe(untilDestroyed(this))
      .subscribe((t4cModel) =>
        this.breadCrumbsService.updatePlaceholder({ t4cModel }),
      );
  }

  ngOnDestroy(): void {
    this.t4cModelService.reset();
    this.breadCrumbsService.updatePlaceholder({ t4cModel: undefined });
  }
}
