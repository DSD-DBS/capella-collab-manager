/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { first } from 'rxjs';
import { ModelDiagramDialogComponent } from 'src/app/projects/models/diagrams/model-diagram-dialog/model-diagram-dialog.component';
import {
  getPrimaryGitModel,
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { TriggerPipelineComponent } from '../../models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { Project, ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  styleUrls: ['./model-overview.component.css'],
})
export class ModelOverviewComponent implements OnInit {
  project?: Project;

  constructor(
    public modelService: ModelService,
    public sessionService: SessionService,
    public projectUserService: ProjectUserService,
    public userService: UserService,
    public projectService: ProjectService,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.project = project));
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
    this.projectService.project$.pipe(first()).subscribe((project) => {
      this.dialog.open(TriggerPipelineComponent, {
        data: { projectSlug: project!.slug, modelSlug: model.slug },
      });
    });
  }

  openDiagramsDialog(model: Model): void {
    this.dialog.open(ModelDiagramDialogComponent, {
      maxWidth: '100vw',
      panelClass: [
        'md:w-[85vw]',
        'md:h-[85vw]',
        'md:max-h-[85vh]',
        'max-h-full',
        'w-full',
        'h-full',
      ],
      data: { modelSlug: model.slug, projectSlug: this.project?.slug },
    });
  }

  getPrimaryGitModelURL(model: Model): string {
    const primaryModel = getPrimaryGitModel(model);
    return primaryModel ? primaryModel.path : '';
  }
}
