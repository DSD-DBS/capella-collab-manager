/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription, combineLatest, filter, map, switchMap } from 'rxjs';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-model-wrapper',
  templateUrl: './model-wrapper.component.html',
  styleUrls: ['./model-wrapper.component.css'],
})
export class ModelWrapperComponent implements OnInit, OnDestroy {
  subscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public modelService: ModelService,
    private projectService: ProjectService,
    private t4cModelService: T4CModelService
  ) {}

  ngOnInit(): void {
    this.subscription = combineLatest([
      this.route.params.pipe(map((params) => params.model as string)),
      this.projectService._project.pipe(
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
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
    this.modelService._model.next(undefined);
    this.t4cModelService._t4cModels.next(undefined);
  }
}
