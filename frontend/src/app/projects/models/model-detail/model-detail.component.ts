/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor, AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from '../../../helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  styleUrls: ['./model-detail.component.css'],
  standalone: true,
  imports: [
    NgIf,
    RouterLink,
    MatRipple,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
    NgFor,
    AsyncPipe,
  ],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  constructor(
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    public userService: UserWrapperService,
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
