/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';

@UntilDestroy()
@Component({
  selector: 'app-provision-workspace',
  templateUrl: './provision-workspace.component.html',
})
export class ProvisionWorkspaceComponent implements OnInit {
  projectSlug?: string;
  projectType?: string;
  models?: Model[];

  public provisionForm = this.fb.group({
    persistentWorkspace: this.fb.control(false),
  });

  constructor(
    private userSessionService: UserSessionService,
    private projectService: ProjectService,
    private modelService: ModelService,
    private sessionService: SessionService,
    private fb: FormBuilder,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.modelService.models$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => (this.models = models));

    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => {
        this.projectType = project.type;
        this.projectSlug = project.slug;
      });

    this.userSessionService.loadSessions();
  }

  requestSessions(): void {
    if (this.projectSlug && this.models) {
      this.sessionService
        .provisionWorkspace(
          this.projectSlug,
          this.models.map((m) => {
            return {
              model_slug: m.slug,
            };
          }),
          true,
        )
        .subscribe(() => {
          this.router.navigateByUrl('/');
        });
    }
  }
}
