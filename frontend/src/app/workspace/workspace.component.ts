/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';

import { NavBarService } from '../general/navbar/service/nav-bar.service';
import { ProjectUserService } from '../projects/project-detail/project-users/service/project-user.service';
import { ProjectUser } from '../schemes';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent {
  repositories: ProjectUser[] = [];
  showSpinner = true;

  constructor(
    public sessionService: SessionService,
    private projectUserService: ProjectUserService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Workspaces';
  }
}
