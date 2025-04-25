/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';

@Component({
  selector: 'app-breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  imports: [RouterLink, AsyncPipe],
})
export class BreadcrumbsComponent {
  constructor(public readonly breadcrumbService: BreadcrumbsService) {}
}
