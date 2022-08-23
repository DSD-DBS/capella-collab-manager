// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnDestroy, OnInit } from '@angular/core';
import { filter, map, Subscription } from 'rxjs';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit, OnDestroy {
  project_slug: string = '';
  project_name: string = '';
  project_subscription?: Subscription;

  constructor(
    private navbarService: NavBarService,
    public projectService: ProjectService
  ) {}

  ngOnInit(): void {
    this.project_subscription = this.projectService._project
      .pipe(
        filter(Boolean),
        map((project) => project.name)
      )
      .subscribe((name) => {
        this.navbarService.title = `Projects / ${name}`;
      });
  }

  ngOnDestroy(): void {
    this.project_subscription?.unsubscribe();
  }
}
