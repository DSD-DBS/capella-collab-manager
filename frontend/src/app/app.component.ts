/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { NavBarService } from './navbar/service/nav-bar.service';
import { ProjectService } from './services/project/project.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit, OnDestroy {
  constructor(
    public navbarService: NavBarService,
    public projectService: ProjectService
  ) {}

  project_list_subscription?: Subscription;

  ngOnInit(): void {
    this.project_list_subscription = this.projectService
      .list()
      .subscribe(this.projectService._projects);
  }

  ngOnDestroy(): void {
    this.project_list_subscription?.unsubscribe();
  }
}
