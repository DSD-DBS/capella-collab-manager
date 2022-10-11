/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-mat-card-overview-loader',
  templateUrl: './mat-card-overview-loader.component.html',
  styleUrls: ['./mat-card-overview-loader.component.css'],
})
export class MatCardOverviewLoaderComponent implements OnInit {
  @Input() loading = true;

  constructor() {}

  ngOnInit(): void {}
}
