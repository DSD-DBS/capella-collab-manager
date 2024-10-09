/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { LicenseUsageWrapperService } from './license-usage.service';

@Component({
  selector: 'app-license-indicator',
  standalone: true,
  imports: [MatIcon, AsyncPipe],
  templateUrl: './license-indicator.component.html',
})
export class LicenseIndicatorComponent {
  constructor(public licenseUsageWrapperService: LicenseUsageWrapperService) {}
}
