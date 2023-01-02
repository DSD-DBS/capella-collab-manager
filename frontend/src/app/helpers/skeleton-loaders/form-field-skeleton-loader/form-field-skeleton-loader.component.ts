/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-form-field-skeleton-loader',
  templateUrl: './form-field-skeleton-loader.component.html',
  styleUrls: ['./form-field-skeleton-loader.component.css'],
})
export class FormFieldSkeletonLoaderComponent {
  constructor() {}

  @Input() loading = true;
}
