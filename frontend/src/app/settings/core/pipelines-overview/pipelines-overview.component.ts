/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import {
  MonitoringService,
  ProjectStatus,
  ToolmodelStatus,
  GeneralHealth,
} from 'src/app/settings/core/pipelines-overview/service/monitoring.service';

@Component({
  selector: 'app-pipelines-overview',
  templateUrl: './pipelines-overview.component.html',
  styleUrls: ['./pipelines-overview.component.css'],
  standalone: true,
  imports: [NgIf, NgxSkeletonLoaderModule, MatIcon, NgFor],
})
export class PipelinesOverviewComponent implements OnInit {
  constructor(private monitoringService: MonitoringService) {}

  toolmodelStatuses?: ToolmodelStatus[];
  projectStatuses?: ProjectStatus[];
  generalHealth?: GeneralHealth;

  ngOnInit(): void {
    this.monitoringService
      .fetchGeneralHealth()
      .subscribe((generalHealth) => (this.generalHealth = generalHealth));

    this.monitoringService
      .fetchProjectHealth()
      .subscribe((projectStatuses) => (this.projectStatuses = projectStatuses));

    this.monitoringService
      .fetchModelHealth()
      .subscribe(
        (toolmodelStatuses) => (this.toolmodelStatuses = toolmodelStatuses),
      );
  }
}
