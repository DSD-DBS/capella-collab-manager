/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { combineLatest, filter, map, Subscription, switchMap } from 'rxjs';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-t4c-model-wrapper',
  templateUrl: './t4c-model-wrapper.component.html',
  styleUrls: ['./t4c-model-wrapper.component.css'],
})
export class T4cModelWrapperComponent implements OnInit, OnDestroy {
  private subscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private t4cModelService: T4CModelService
  ) {}

  ngOnInit(): void {
    this.subscription = combineLatest([
      this.projectService._project.pipe(
        filter(Boolean),
        map((project) => project.slug)
      ),
      this.modelService._model.pipe(
        filter(Boolean),
        map((model) => model.slug)
      ),
      this.route.params.pipe(map((params) => parseInt(params.t4c_model_id))),
    ])
      .pipe(
        switchMap((res: [string, string, number]) =>
          this.t4cModelService.getT4CModel(...res)
        )
      )
      .subscribe((t4cModel) => {
        this.t4cModelService._t4cModel.next(t4cModel);
      });
  }

  ngOnDestroy(): void {
    this.t4cModelService._t4cModel.next(undefined);
    this.subscription?.unsubscribe();
  }
}
