/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgClass } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { T4CLicenseServerUsage } from '../../openapi';
import { LicenseUsageWrapperService } from './license-usage.service';

@Component({
  selector: 'app-license-indicator',
  imports: [MatIcon, AsyncPipe, NgClass],
  templateUrl: './license-indicator.component.html',
})
export class LicenseIndicatorComponent {
  licenseUsageWrapperService = inject(LicenseUsageWrapperService);

  getLevel(usage: T4CLicenseServerUsage) {
    const usagePercentage = (usage.total - usage.free) / usage.total;
    return this.levels.find(
      (level) => usagePercentage * 100 >= level.percentage,
    );
  }

  levels = [
    {
      percentage: 100,
      text: 'All TeamForCapella licenses are currently in use. You can start new sessions, but may encounter the error "Invalid license" when trying to use TeamForCapella. Please make sure to terminate your sessions after use.',
      icon: 'error',
      classes: 'bg-(--error-color) text-white',
    },
    {
      percentage: 75,
      text: 'Most TeamForCapella licenses are currently in use. Please make sure to terminate your sessions after use.',
      icon: 'warning',
      classes: 'bg-(--warning-color) text-white',
    },
    {
      percentage: 0,
      text: 'TeamForCapella licenses are available. We do not expect any license issues in the session.',
      icon: 'check_circle',
      classes: '',
    },
  ];
}
