/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { MatIconComponent } from 'src/app/helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from 'src/app/helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-instances/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-git-instances',
  templateUrl: './git-instances.component.html',
  imports: [
    RouterLink,
    FormsModule,
    ReactiveFormsModule,
    AsyncPipe,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
  ],
})
export class GitInstancesComponent implements OnInit {
  gitInstancesService = inject(GitInstancesWrapperService);

  ngOnInit(): void {
    this.gitInstancesService.loadGitInstances();
  }
}
