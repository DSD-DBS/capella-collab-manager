/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { T4CRepoService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import {
  T4CModel,
  T4cModelService,
} from 'src/app/services/source/t4c-model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';
import { map, combineLatest, switchMap, filter, tap, Observable } from 'rxjs';

@Component({
  selector: 'app-t4c-model-wrapper',
  templateUrl: './t4c-model-wrapper.component.html',
  styleUrls: ['./t4c-model-wrapper.component.css'],
})
export class T4cModelWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private route: ActivatedRoute,
    private projectService: ProjectService,
    private modelService: ModelService,
    private t4cModelService: T4cModelService
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.projectService._project.pipe(
        filter(Boolean),
        map((p) => p.slug)
      ),
      this.modelService._model.pipe(
        filter(Boolean),
        map((m) => m.slug)
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
  }
}
