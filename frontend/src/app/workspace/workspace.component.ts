/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';

import { NavBarService } from '../general/navbar/service/nav-bar.service';
import { Project } from 'src/app/services/project/project.service';
import { DepthType, SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent {
  repositories: Project[] = [];
  showSpinner = true;
  canCreateSession = true;

  constructor(
    public sessionService: SessionService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Workspaces';
  }

  ngOnInit() {}

  requestSession() {
    var depth = DepthType.CompleteHistory;
    this.canCreateSession = false;
    this.sessionService
      .createNewSession('persistent', undefined, '', depth)
      .subscribe(
        (res) => {
          this.canCreateSession = true;
        },
        () => {
          this.canCreateSession = true;
        }
      );
  }
}
