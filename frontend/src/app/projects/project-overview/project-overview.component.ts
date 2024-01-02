/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ProjectService, UserMetadata } from '../service/project.service';

@Component({
  selector: 'app-project-overview',
  templateUrl: './project-overview.component.html',
  styleUrls: ['./project-overview.component.css'],
})
export class ProjectOverviewComponent implements OnInit {
  constructor(public projectService: ProjectService) {}

  ngOnInit() {
    this.projectService.loadProjects();
  }

  sumUsers(user: UserMetadata): number {
    return user.contributors + user.leads + user.subscribers;
  }
}
