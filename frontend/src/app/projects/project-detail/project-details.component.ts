/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';

import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectService } from '../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent implements OnInit {
  projectType?: string;

  constructor(
    public projectService: ProjectService,
    public projectUserService: ProjectUserService,
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => (this.projectType = project.type));
  }
}
