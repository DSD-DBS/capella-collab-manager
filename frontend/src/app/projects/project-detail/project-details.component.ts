// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { ProjectService } from '../service/project.service';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit {
  project: string = '';

  constructor(
    private route: ActivatedRoute,
    private navbarService: NavBarService,
    private projectService: ProjectService
  ) {
    this.navbarService.title = 'Projects / options';
    this.projectService.project = null;
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.project = params['project'];
      this.navbarService.title = 'Projects / ' + this.project;
      this.projectService.getProject(this.project).subscribe({
        next: (res) => {
          this.projectService.project = res;
        },
        error: () => {},
      });
    });
  }
}
