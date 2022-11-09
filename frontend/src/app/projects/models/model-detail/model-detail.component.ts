/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { BehaviorSubject, filter, Subscription } from 'rxjs';
import { ModelService } from 'src/app/services/model/model.service';
import {
  T4CModel,
  T4CModelService,
} from 'src/app/services/modelsources/t4c-model/t4c-model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  GetGitModel,
  GitModelService,
} from '../../project-detail/model-overview/model-detail/git-model.service';

@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  public gitModels: Array<GetGitModel> = [];
  private _t4cModels = new BehaviorSubject<T4CModel[] | undefined>(undefined);
  public t4cModels: T4CModel[] = [];

  private gitModelsSubscription?: Subscription;
  private t4cModelsSubscription?: Subscription;

  constructor(
    private gitModelService: GitModelService,
    public modelService: ModelService,
    public projectService: ProjectService,
    private t4cModelService: T4CModelService
  ) {}

  ngOnInit(): void {
    this.gitModelsSubscription = this.gitModelService.gitModels.subscribe(
      (gitModels) => (this.gitModels = gitModels)
    );

    this._t4cModels.pipe(filter(Boolean)).subscribe((models) => {
      this.t4cModels = models;
    });

    this.t4cModelsSubscription = this.t4cModelService
      .listT4CModels(
        this.projectService.project!.slug,
        this.modelService.model!.slug
      )
      .subscribe((models) => {
        this._t4cModels.next(models);
      });

    this.gitModelService.loadGitModels(
      this.projectService.project!.slug,
      this.modelService.model!.slug
    );
  }

  ngOnDestroy(): void {
    this.gitModelsSubscription?.unsubscribe();
  }
}
