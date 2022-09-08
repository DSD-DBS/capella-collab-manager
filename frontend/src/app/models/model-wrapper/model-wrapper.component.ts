/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { combineLatest, map, Subscription, switchMap, filter } from 'rxjs';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-model-wrapper',
  templateUrl: './model-wrapper.component.html',
  styleUrls: ['./model-wrapper.component.css'],
})
export class ModelWrapperComponent implements OnInit, OnDestroy {
  modelSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public modelService: ModelService,
    private projectService: ProjectService
  ) {}

  ngOnInit(): void {
    this.modelSubscription = combineLatest([
      this.route.params.pipe(map((params) => params.model as string)),
      this.projectService._project.pipe(
        filter(Boolean),
        map((project) => project.slug)
      ),
    ])
      .pipe(switchMap((args) => this.modelService.getModelBySlug(...args)))
      .subscribe(this.modelService._model);
  }

  ngOnDestroy(): void {
    this.modelSubscription?.unsubscribe();
    this.modelService._model.next(undefined);
  }
}
