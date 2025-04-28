/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  MatAnchor,
  MatButton,
  MatMiniFabAnchor,
  MatMiniFabButton,
} from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltip } from '@angular/material/tooltip';
import { Router, RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { first, filter } from 'rxjs';
import { Project, ToolModel } from 'src/app/openapi';
import { ModelDiagramDialogComponent } from 'src/app/projects/models/diagrams/model-diagram-dialog/model-diagram-dialog.component';
import {
  getPrimaryGitModel,
  ModelWrapperService,
} from 'src/app/projects/models/service/model.service';
import { MoveModelComponent } from 'src/app/projects/project-detail/model-overview/move-model/move-model.component';
import { ReorderModelsDialogComponent } from 'src/app/projects/project-detail/model-overview/reorder-models-dialog/reorder-models-dialog.component';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { CreatePersistentSessionDialogComponent } from '../../../sessions/user-sessions-wrapper/create-sessions/create-persistent-session/create-persistent-session-dialog/create-persistent-session-dialog.component';
import { TriggerPipelineComponent } from '../../models/backup-settings/trigger-pipeline/trigger-pipeline.component';
import { ProjectWrapperService } from '../../service/project.service';
import { ModelComplexityBadgeComponent } from './model-complexity-badge/model-complexity-badge.component';

@UntilDestroy()
@Component({
  selector: 'app-model-overview',
  templateUrl: './model-overview.component.html',
  imports: [
    MatAnchor,
    RouterLink,
    MatTooltip,
    MatIcon,
    MatButton,
    NgxSkeletonLoaderModule,
    ModelComplexityBadgeComponent,
    MatMiniFabAnchor,
    MatMiniFabButton,
    AsyncPipe,
    MatMenuModule,
  ],
})
export class ModelOverviewComponent implements OnInit {
  modelService = inject(ModelWrapperService);
  sessionService = inject(SessionService);
  projectUserService = inject(ProjectUserService);
  userService = inject(OwnUserWrapperService);
  projectService = inject(ProjectWrapperService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  project?: Project;
  models?: ToolModel[];

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.project = project));

    this.modelService.models$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => {
        this.models = models.sort((a, b) => {
          if (a.display_order && b.display_order) {
            return a.display_order - b.display_order;
          }
          return b.id - a.id;
        });
      });
  }

  getPrimaryWorkingMode(model: ToolModel): string {
    if (model.t4c_models?.length) {
      return 'T4C';
    } else if (model.git_models?.length) {
      return 'Git';
    }
    return 'Unset';
  }

  openPipelineDialog(model: ToolModel): void {
    this.projectService.project$.pipe(first()).subscribe((project) => {
      this.dialog.open(TriggerPipelineComponent, {
        data: { projectSlug: project!.slug, modelSlug: model.slug },
      });
    });
  }

  openDiagramsDialog(model: ToolModel): void {
    this.dialog.open(ModelDiagramDialogComponent, {
      maxWidth: '100dvw',
      maxHeight: '100dvh',
      data: { model: model, project: this.project },
    });
  }

  getPrimaryGitModelURL(model: ToolModel): string {
    const primaryModel = getPrimaryGitModel(model);
    return primaryModel ? primaryModel.path : '';
  }

  openMoveToProjectDialog(model: ToolModel): void {
    this.dialog.open(MoveModelComponent, {
      maxWidth: '100vw',
      maxHeight: '200vw',
      data: { projectSlug: this.project?.slug, model: model },
    });
  }

  openPersistentSessionDialog(model: ToolModel): void {
    const dialogRef = this.dialog.open(CreatePersistentSessionDialogComponent, {
      data: {
        toolVersion: model.version,
        tool: model.tool,
      },
    });
    dialogRef.afterClosed().subscribe((success) => {
      if (success) {
        this.router.navigate(['/']);
      }
    });
  }

  openReorderModelsDialog(models: ToolModel[]): void {
    if (this.project) {
      this.dialog.open(ReorderModelsDialogComponent, {
        data: { projectSlug: this.project.slug, models: models },
      });
    }
  }
}
