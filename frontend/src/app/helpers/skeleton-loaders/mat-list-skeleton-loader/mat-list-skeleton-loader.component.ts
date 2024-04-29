/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgFor } from '@angular/common';
import { Component, Input } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-mat-list-skeleton-loader',
  templateUrl: './mat-list-skeleton-loader.component.html',
  styleUrls: ['./mat-list-skeleton-loader.component.css'],
  standalone: true,
  imports: [NgFor, NgxSkeletonLoaderModule],
})
export class MatListSkeletonLoaderComponent {
  _listNumberArray: number[] = [];

  @Input()
  set listNumber(value: number) {
    this._listNumberArray = [...Array(value).keys()];
  }
}
