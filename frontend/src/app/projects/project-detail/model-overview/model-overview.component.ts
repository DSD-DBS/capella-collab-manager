/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { NewReadonlySessionDialogComponent } from 'src/app/sessions/new-readonly-session-dialog/new-readonly-session-dialog.component';
import { SessionService } from 'src/app/sessions/service/session.service';
import { TriggerPipelineComponent } from '../../models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { Project } from '../../service/project.service';

@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  styleUrls: ['./model-overview.component.css'],
})
export class ModelOverviewComponent implements OnInit {
  @Input() project!: Project;
  models?: Model[];

  constructor(
    public modelService: ModelService,
    private dialog: MatDialog,
    public sessionService: SessionService,
    public projectUserService: ProjectUserService,
    public userService: UserService
  ) {}

  ngOnInit(): void {
    this.modelService._models.pipe().subscribe((models) => {
      this.models = models;
    });
  }

  getPrimaryWorkingMode(model: Model): string {
    if (model.t4c_models.length) {
      return 'T4C';
    } else if (model.git_models.length) {
      return 'Git';
    }
    return 'Unset';
  }

  openPipelineDialog(model: Model): void {
    this.dialog.open(TriggerPipelineComponent, {
      data: { project: this.project, model: model },
    });
  }

  getPrimaryGitModelURL(model: Model): string {
    const primaryModel = model.git_models.find((gitModel) => gitModel.primary);
    if (primaryModel) {
      return primaryModel.path;
    } else {
      return '';
    }
  }

  newReadonlySession(model: Model) {
    this.dialog.open(NewReadonlySessionDialogComponent, {
      data: { project: this.project, model: model },
    });
  }
}
