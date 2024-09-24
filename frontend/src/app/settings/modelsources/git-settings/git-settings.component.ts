/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {
  MatIconAnchor,
  MatIconButton,
  MatButton,
} from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { MatIconComponent } from 'src/app/helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from 'src/app/helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  standalone: true,
  imports: [
    MatIconAnchor,
    RouterLink,
    MatIcon,
    MatIconButton,
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatInput,
    MatError,
    MatButton,
    AsyncPipe,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
  ],
})
export class GitSettingsComponent implements OnInit {
  constructor(public gitInstancesService: GitInstancesWrapperService) {}

  ngOnInit(): void {
    this.gitInstancesService.loadGitInstances();
  }
}
