/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import {
  T4CModel,
  T4CModelService,
} from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import {
  GetGitModel,
  GitModelService,
} from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  public gitModels?: GetGitModel[] = undefined;
  public t4cModels?: T4CModel[] = undefined;

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

    this.t4cModelsSubscription = this.t4cModelService
      .listT4CModels(
        this.projectService.project!.slug,
        this.modelService.model!.slug
      )
      .subscribe((models) => (this.t4cModels = models));

    this.gitModelService.loadGitModels(
      this.projectService.project!.slug,
      this.modelService.model!.slug
    );
  }

  ngOnDestroy(): void {
    this.gitModelsSubscription?.unsubscribe();
    this.gitModelService.clear();
    this.t4cModelsSubscription?.unsubscribe();
    this.t4cModelService.clear();
  }
}
