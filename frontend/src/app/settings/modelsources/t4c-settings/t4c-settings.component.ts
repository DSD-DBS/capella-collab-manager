/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { MatCardOverviewSkeletonLoaderComponent } from 'src/app/helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';
import { T4CLicenseServerWrapperService } from '../../../services/settings/t4c-license-server.service';

@Component({
  selector: 'app-t4c-settings',
  templateUrl: './t4c-settings.component.html',
  styleUrls: ['./t4c-settings.component.css'],
  imports: [
    RouterLink,
    MatRipple,
    MatIconComponent,
    NgClass,
    MatIcon,
    AsyncPipe,
    MatCardOverviewSkeletonLoaderComponent,
  ],
})
export class T4CSettingsComponent {
  t4cInstanceService = inject(T4CInstanceWrapperService);
  t4cLicenseServerService = inject(T4CLicenseServerWrapperService);
}
