/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { Router } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { RelativeTimeComponent } from 'src/app/general/relative-time/relative-time.component';
import {
  Pipeline,
  PipelineRun,
  ProjectsModelsBackupsService,
} from 'src/app/openapi';
import { PipelineDeletionDialogComponent } from 'src/app/projects/models/backup-settings/pipeline-deletion-dialog/pipeline-deletion-dialog.component';
import { SessionService } from 'src/app/sessions/service/session.service';
import { CreateBackupComponent } from '../create-backup/create-backup.component';
import { PipelineWrapperService } from '../service/pipeline.service';

@Component({
  selector: 'app-trigger-pipeline',
  templateUrl: './trigger-pipeline.component.html',
  imports: [
    MatIcon,
    ReactiveFormsModule,
    MatButton,
    AsyncPipe,
    NgxSkeletonLoaderModule,
    RelativeTimeComponent,
  ],
})
export class TriggerPipelineComponent implements OnInit {
  private dialogRef =
    inject<MatDialogRef<TriggerPipelineComponent>>(MatDialogRef);
  data = inject<{
    projectSlug: string;
    modelSlug: string;
  }>(MAT_DIALOG_DATA);
  dialog = inject(MatDialog);
  pipelineWrapperService = inject(PipelineWrapperService);
  private pipelinesService = inject(ProjectsModelsBackupsService);
  sessionService = inject(SessionService);
  private router = inject(Router);

  ngOnInit(): void {
    this.pipelineWrapperService
      .loadPipelines(this.data.projectSlug, this.data.modelSlug)
      .subscribe();
  }

  runPipeline(pipeline: Pipeline) {
    this.pipelinesService
      .createPipelineRun(
        this.data.projectSlug,
        pipeline.id,
        this.data.modelSlug,
      )
      .subscribe((pipelineRun: PipelineRun) => {
        this.closeDialog();
        this.router.navigate([
          'project',
          this.data.projectSlug,
          'model',
          this.data.modelSlug,
          'pipeline',
          pipeline.id,
          'run',
          pipelineRun.id,
        ]);
      });
  }

  closeDialog(): void {
    this.dialogRef.close();
  }

  removePipeline(backup: Pipeline): void {
    this.dialog.open(PipelineDeletionDialogComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
        backup,
      },
    });
  }

  openPipelineRuns(backup: Pipeline): void {
    this.closeDialog();
    this.router.navigate([
      'project',
      this.data.projectSlug,
      'model',
      this.data.modelSlug,
      'pipeline',
      backup.id,
      'runs',
    ]);
  }

  createPipeline(): void {
    const dialogRef = this.dialog.open(CreateBackupComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
      },
    });

    dialogRef.afterClosed().subscribe((success) => {
      if (success) {
        this.pipelineWrapperService
          .loadPipelines(this.data.projectSlug, this.data.modelSlug)
          .subscribe();
      }
    });
  }

  isBeforeCurrentTime(date: string): boolean {
    const nextRunDate = new Date(date);
    const currentDate = new Date();
    return nextRunDate < currentDate;
  }
}
