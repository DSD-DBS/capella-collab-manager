/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { combineLatest, filter, map, switchMap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy({ checkProperties: true })
@Component({
  selector: 'app-model-wrapper',
  templateUrl: './model-wrapper.component.html',
  styleUrls: ['./model-wrapper.component.css'],
})
export class ModelWrapperComponent implements OnInit, OnDestroy {
  breadcrumbSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public modelService: ModelService,
    private projectService: ProjectService,
    private t4cModelService: T4CModelService,
    private breadcrumbService: BreadcrumbsService
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.route.params.pipe(map((params) => params.model as string)),
      this.projectService.project.pipe(
        filter(Boolean),
        map((project) => project.slug)
      ),
    ])
      .pipe(switchMap((args) => this.modelService.getModelBySlug(...args)))
      .subscribe({
        next: this.modelService._model.next.bind(this.modelService._model),
        error: (_) => {
          this.modelService._model.next(undefined);
        },
      });

    this.breadcrumbSubscription = this.modelService._model.subscribe((model) =>
      this.breadcrumbService.updatePlaceholder({ model })
    );
  }

  ngOnDestroy(): void {
    this.breadcrumbSubscription?.unsubscribe();
    this.breadcrumbService.updatePlaceholder({ model: undefined });
    this.modelService._model.next(undefined);
    this.t4cModelService._t4cModels.next(undefined);
  }
}
