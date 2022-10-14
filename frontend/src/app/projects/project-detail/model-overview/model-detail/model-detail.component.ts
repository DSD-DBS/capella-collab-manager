/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { GetGitModel } from 'src/app/services/source/source.service';
import { GitModelService } from './git-model.service';

@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
})
export class ModelDetailComponent implements OnInit {
  public gitModels: Array<GetGitModel> = [];

  private gitModelsSubscription?: Subscription;

  constructor(
    private gitModelService: GitModelService,
    public modelService: ModelService,
    public projectService: ProjectService
  ) {}

  ngOnInit(): void {
    this.gitModelsSubscription = this.gitModelService.gitModels.subscribe(
      (gitModels) => (this.gitModels = gitModels)
    );

    this.gitModelService.loadGitModels(
      this.projectService.project!.slug,
      this.modelService.model!.slug
    );
  }

  ngOnDestroy(): void {
    this.gitModelsSubscription?.unsubscribe();
  }
}
