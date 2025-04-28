/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgFor, AsyncPipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from '../../../helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-detail',
  templateUrl: './model-detail.component.html',
  imports: [
    RouterLink,
    MatRipple,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
    NgFor,
    AsyncPipe,
    MatIconModule,
  ],
})
export class ModelDetailComponent implements OnInit, OnDestroy {
  projectService = inject(ProjectWrapperService);
  modelService = inject(ModelWrapperService);
  gitModelService = inject(GitModelService);
  t4cModelService = inject(T4CModelService);
  userService = inject(OwnUserWrapperService);

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
