/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, Inject, OnInit } from '@angular/core';
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
import {
  Backup,
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
  ],
})
export class TriggerPipelineComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<TriggerPipelineComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string },
    public dialog: MatDialog,
    public pipelineWrapperService: PipelineWrapperService,
    private pipelinesService: ProjectsModelsBackupsService,
    public sessionService: SessionService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.pipelineWrapperService
      .loadPipelines(this.data.projectSlug, this.data.modelSlug)
      .subscribe();
  }

  runPipeline(pipeline: Backup) {
    this.pipelinesService
      .createPipelineRun(
        this.data.projectSlug,
        pipeline.id,
        this.data.modelSlug,
        {
          include_commit_history: false,
        },
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
          'logs',
        ]);
      });
  }

  closeDialog(): void {
    this.dialogRef.close();
  }

  removePipeline(backup: Backup): void {
    this.dialog.open(PipelineDeletionDialogComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
        backup,
      },
    });
  }

  openPipelineRuns(backup: Backup): void {
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
}
