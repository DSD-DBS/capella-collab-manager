/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest } from 'rxjs';
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

@UntilDestroy()
@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  public gitModels?: GetGitModel[] = undefined;
  public t4cModels?: T4CModel[] = undefined;

  constructor(
    private gitModelService: GitModelService,
    public modelService: ModelService,
    public projectService: ProjectService,
    private t4cModelService: T4CModelService
  ) {}

  ngOnInit(): void {
    this.gitModelService.gitModels
      .pipe(untilDestroyed(this))
      .subscribe((gitModels) => (this.gitModels = gitModels));

    combineLatest([this.projectService.project, this.modelService.model])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.t4cModelService
          .listT4CModels(project?.slug!, model?.slug!)
          .subscribe((models) => (this.t4cModels = models));

        this.gitModelService.loadGitModels(project?.slug!, model?.slug!);
      });
  }

  ngOnDestroy(): void {
    this.gitModelService.clear();
    this.t4cModelService.clear();
  }
}
