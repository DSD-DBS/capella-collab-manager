/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription, filter, map } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit, OnDestroy {
  projectSubscription?: Subscription;

  constructor(
    private navbarService: NavBarService,
    public projectService: ProjectService,
    public projectUserService: ProjectUserService,
    public activatedRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.projectSubscription = this.projectService._project
      .pipe(
        filter(Boolean),
        map((project) => project.name)
      )
      .subscribe((name) => {
        this.navbarService.title = `Projects / ${name}`;
      });
  }

  ngOnDestroy(): void {
    this.projectSubscription?.unsubscribe();
  }
}
