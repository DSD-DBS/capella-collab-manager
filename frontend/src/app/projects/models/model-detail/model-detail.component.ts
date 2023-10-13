/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { UserService } from 'src/app/services/user/user.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    public userService: UserService,
  ) {}

  ngOnInit(): void {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.t4cModelService.loadT4CModels(project.slug, model.slug);
        this.gitModelService.loadGitModels(project.slug, model.slug);
      });
  }

  ngOnDestroy(): void {
    this.gitModelService.reset();
    this.t4cModelService.reset();
  }
}
