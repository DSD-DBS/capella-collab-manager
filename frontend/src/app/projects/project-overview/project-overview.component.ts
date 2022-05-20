// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { Project, ProjectService } from '../service/project.service';

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
    this.projectService.getProjects().subscribe({
      next: (res) => {
        this.projects = res;
        this.showSpinner = false;
      },
      error: () => {
        this.showSpinner = false;
      },
    });
  }
}
