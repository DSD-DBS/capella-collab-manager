/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-button-skeleton-loader',
  templateUrl: './button-skeleton-loader.component.html',
  styleUrls: ['./button-skeleton-loader.component.css'],
})
export class ButtonSkeletonLoaderComponent {
  @Input() loading = true;
}
