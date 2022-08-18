// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit {
  project_slug: string = '';
  project_name: string = '';
  isStaged: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private navbarService: NavBarService,
    private projectService: ProjectService
  ) {
    this.navbarService.title = 'Projects / loading';
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.project_slug = params['project'];
      this.projectService.init(params['project']).subscribe({
        next: (project) => {
          this.project_name = project.name;
          this.navbarService.title = 'Projects / ' + this.project_name;
        },
        error: () => {},
      });
      this.projectService
        .getProjectBySlug(this.project_slug)
        .subscribe((project: Project) => {
          this.isStaged = project.staged_by ? true : false;
        });
    });
  }
}
