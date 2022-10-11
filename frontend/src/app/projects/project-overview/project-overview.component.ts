/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { tap } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import {
  ProjectService,
  UserMetadata,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-overview',
  templateUrl: './project-overview.component.html',
  styleUrls: ['./project-overview.component.css'],
})
export class ProjectOverviewComponent implements OnInit {
  loading = true;

  constructor(
    public projectService: ProjectService,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Projects';
  }

  ngOnInit() {
    this.navbarService.enableAll();
    const projects = this.projectService._projects;
    this.projectService
      .list()
      .pipe(
        tap(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: projects.next.bind(projects),
        error: projects.error.bind(projects),
      });
  }

  sumUsers(user: UserMetadata): number {
    return user.contributors + user.leads + user.subscribers;
  }
}
