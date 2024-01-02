/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-wrapper',
  templateUrl: './model-wrapper.component.html',
  styleUrls: ['./model-wrapper.component.css'],
})
export class ModelWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private route: ActivatedRoute,
    public modelService: ModelService,
    private projectService: ProjectService,
    private t4cModelService: T4CModelService,
    private breadcrumbService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.route.params.pipe(map((params) => params.model as string)),
      this.projectService.project$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([modelSlug, project]) =>
        this.modelService.loadModelbySlug(modelSlug, project.slug),
      );

    this.modelService.model$
      .pipe(untilDestroyed(this))
      .subscribe((model) =>
        this.breadcrumbService.updatePlaceholder({ model }),
      );
  }

  ngOnDestroy(): void {
    this.breadcrumbService.updatePlaceholder({ model: undefined });
    this.modelService.clearModel();
    this.t4cModelService.reset();
  }
}
