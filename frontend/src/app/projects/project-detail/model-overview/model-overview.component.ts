/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { first } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { CreateReadonlySessionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/create-session/create-readonly-session-dialog/create-readonly-session-dialog.component';
import { TriggerPipelineComponent } from '../../models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  styleUrls: ['./model-overview.component.css'],
})
export class ModelOverviewComponent {
  constructor(
    public modelService: ModelService,
    public sessionService: SessionService,
    public projectUserService: ProjectUserService,
    public userService: UserService,
    public projectService: ProjectService,
    private dialog: MatDialog
  ) {}

  getPrimaryWorkingMode(model: Model): string {
    if (model.t4c_models.length) {
      return 'T4C';
    } else if (model.git_models.length) {
      return 'Git';
    }
    return 'Unset';
  }

  openPipelineDialog(model: Model): void {
    this.projectService.project.pipe(first()).subscribe((project) => {
      this.dialog.open(TriggerPipelineComponent, {
        data: { projectSlug: project!.slug, modelSlug: model.slug },
      });
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
    this.projectService.project.pipe(first()).subscribe((project) => {
      this.dialog.open(CreateReadonlySessionDialogComponent, {
        data: { projectSlug: project!.slug, model: model },
      });
    });
  }
}
