/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
import { NavBarService } from '../navbar/service/nav-bar.service';
import { SessionService } from '../services/session/session.service';
import { ProjectUser } from '../schemes';
import { ProjectUserService } from '../projects/project-detail/project-users/service/project-user.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent implements OnInit {
  repositories: Array<ProjectUser> = [];
  showSpinner = true;

  constructor(
    public sessionService: SessionService,
    private projectUserService: ProjectUserService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Workspaces';
  }

  ngOnInit() {
    // FIXME: Fetch project users
    // this.showSpinner = true;
    // this.projectUserService.subscribe({
    //   next: (res) => {
    //     this.repositories = res;
    //     this.showSpinner = false;
    //   },
    //   error: () => {
    //     this.showSpinner = false;
    //   },
    // });
  }
}
