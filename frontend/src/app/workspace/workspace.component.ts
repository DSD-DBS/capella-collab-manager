// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from '../navbar/service/nav-bar.service';
import { Project, ProjectService } from '../projects/service/project.service';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent implements OnInit {
  repositories: Array<Project> = [];
  showSpinner = true;

  constructor(
    public sessionService: SessionService,
    private projectService: ProjectService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Workspaces';
  }

  ngOnInit() {
    this.showSpinner = true;
    this.projectService.list().subscribe({
      next: (res) => {
        this.repositories = res;
        this.showSpinner = false;
      },
      error: () => {
        this.showSpinner = false;
      },
    });
  }
}
