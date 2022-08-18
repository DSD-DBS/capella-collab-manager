/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { NavBarService } from './navbar/service/nav-bar.service';
import { ProjectService } from './services/project/project.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  constructor(
    public navbarService: NavBarService,
    public projectService: ProjectService
  ) {}

  ngOnInit(): void {
    let projects = this.projectService._projects;
    this.projectService.list().subscribe({
      next: projects.next.bind(projects),
      error: projects.error.bind(projects),
    });
  }
}
