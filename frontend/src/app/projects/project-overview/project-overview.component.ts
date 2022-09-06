/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import {
  Project,
  ProjectService,
  UserMetadata,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-overview',
  templateUrl: './project-overview.component.html',
  styleUrls: ['./project-overview.component.css'],
})
export class ProjectOverviewComponent implements OnInit {
  projects: Array<Project> = [];
  showSpinner = true;

  constructor(
    private projectService: ProjectService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Projects';
    this.navbarService.enableAll();
  }

  ngOnInit() {
    this.showSpinner = true;
    this.projectService.initAll().subscribe({
      next: (res) => {
        this.projects = this.sortProject(res);
        this.showSpinner = false;
      },
      error: () => {
        this.showSpinner = false;
      },
    });
  }

  sortProject(projects: Array<Project>): Array<Project> {
    // Sort projects by user count
    return projects.sort((a: Project, b: Project) => {
      return this.sumUsers(b.users) - this.sumUsers(a.users);
    });
  }

  sumUsers(user: UserMetadata): number {
    return user.contributors + user.leads + user.subscribers;
  }
}
