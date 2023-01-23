/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { tap } from 'rxjs';
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

  constructor(public projectService: ProjectService) {}

  ngOnInit() {
    this.projectService
      .list()
      .pipe(tap(() => (this.loading = false)))
      .subscribe();
  }

  sumUsers(user: UserMetadata): number {
    return user.contributors + user.leads + user.subscribers;
  }
}
