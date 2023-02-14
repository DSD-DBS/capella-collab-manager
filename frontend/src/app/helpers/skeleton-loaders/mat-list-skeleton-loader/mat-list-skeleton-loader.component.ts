/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-mat-list-skeleton-loader',
  templateUrl: './mat-list-skeleton-loader.component.html',
  styleUrls: ['./mat-list-skeleton-loader.component.css'],
})
export class MatListSkeletonLoaderComponent {
  _listNumberArray: number[] = [];

  @Input()
  set listNumber(value: number) {
    this._listNumberArray = [...Array(value).keys()];
  }
}
