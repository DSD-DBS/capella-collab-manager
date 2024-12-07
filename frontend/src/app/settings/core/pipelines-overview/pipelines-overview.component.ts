/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import {
  HealthService,
  ProjectStatus,
  StatusResponse,
  ToolmodelStatus,
} from 'src/app/openapi';

@Component({
  selector: 'app-pipelines-overview',
  templateUrl: './pipelines-overview.component.html',
  styleUrls: ['./pipelines-overview.component.css'],
  imports: [NgxSkeletonLoaderModule, MatIcon],
})
export class PipelinesOverviewComponent implements OnInit {
  constructor(private healthService: HealthService) {}

  toolmodelStatuses?: ToolmodelStatus[];
  projectStatuses?: ProjectStatus[];
  generalHealth?: StatusResponse;

  ngOnInit(): void {
    this.healthService
      .generalStatus()
      .subscribe((generalHealth) => (this.generalHealth = generalHealth));

    this.healthService
      .projectStatus()
      .subscribe((projectStatuses) => (this.projectStatuses = projectStatuses));

    this.healthService
      .modelStatus()
      .subscribe(
        (toolmodelStatuses) => (this.toolmodelStatuses = toolmodelStatuses),
      );
  }
}
