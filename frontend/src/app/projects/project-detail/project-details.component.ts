/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { Subscription, filter, map } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectService } from '../service/project.service';

@UntilDestroy({ checkProperties: true })
@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css'],
})
export class ProjectDetailsComponent {
  projectSubscription?: Subscription;

  constructor(
    public projectService: ProjectService,
    public projectUserService: ProjectUserService,
    public activatedRoute: ActivatedRoute
  ) {}
}
