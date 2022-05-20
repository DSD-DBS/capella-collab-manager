// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';

@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit {
  project: string = '';

  constructor(
    private route: ActivatedRoute,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Projects / options';
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.project = params['project'];
      this.navbarService.title = 'Projects / ' + this.project;
    });
  }
}
