/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { Observable } from 'rxjs';

import {
  Breadcrumb,
  BreadcrumbsService,
} from 'src/app/general/breadcrumbs/breadcrumbs.service';

@Component({
  selector: 'app-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.css'],
})
export class BreadcrumbsComponent {
  breadcrumbs: Observable<Breadcrumb[]>;

  constructor(private readonly breadcrumbService: BreadcrumbsService) {
    this.breadcrumbs = breadcrumbService.breadcrumbs;
  }
}
