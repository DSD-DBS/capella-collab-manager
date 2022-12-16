/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-button-skeleton-loader',
  templateUrl: './button-skeleton-loader.component.html',
  styleUrls: ['./button-skeleton-loader.component.css'],
})
export class ButtonSkeletonLoaderComponent {
  constructor() {}

  @Input() loading = true;
}
