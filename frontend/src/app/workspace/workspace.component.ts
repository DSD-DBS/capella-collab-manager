// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import {
  Project,
  ProjectService,
} from '../services/repository/repository.service';
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
    private projectService: ProjectService
  ) {}

  ngOnInit() {
    this.showSpinner = true;
    this.projectService.getProjects().subscribe({
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
