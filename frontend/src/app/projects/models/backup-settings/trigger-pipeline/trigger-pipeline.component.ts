/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AsyncPipe } from '@angular/common';
import { Component, Inject, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatIconAnchor, MatButton, MatAnchor } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatRipple } from '@angular/material/core';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatSlideToggle } from '@angular/material/slide-toggle';
import { MatTooltip } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  PipelineRun,
  PipelineRunService,
} from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { CreateBackupComponent } from '../create-backup/create-backup.component';
import { PipelineService, Pipeline } from '../service/pipeline.service';
import {
  ViewLogsDialogComponent,
  ViewLogsData,
} from '../view-logs-dialog/view-logs-dialog.component';

@Component({
  selector: 'app-trigger-pipeline',
  templateUrl: './trigger-pipeline.component.html',
  standalone: true,
  imports: [
    MatIconAnchor,
    MatIcon,
    MatRipple,
    FormsModule,
    ReactiveFormsModule,
    MatCheckbox,
    MatButton,
    MatAnchor,
    MatSlideToggle,
    MatTooltip,
    AsyncPipe,
    NgxSkeletonLoaderModule,
  ],
})
export class TriggerPipelineComponent implements OnInit {
  selectedPipeline?: Pipeline = undefined;

  force = false;

  configurationForm = new FormGroup({
    includeHistory: new FormControl(false),
  });

  constructor(
    private toastService: ToastService,
    private dialogRef: MatDialogRef<TriggerPipelineComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string },
    public dialog: MatDialog,
    public pipelineService: PipelineService,
    private pipelineRunService: PipelineRunService,
    public sessionService: SessionService,
    public userService: UserWrapperService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.pipelineService
      .loadPipelines(this.data.projectSlug, this.data.modelSlug)
      .subscribe();
  }

  selectPipeline(pipeline: Pipeline) {
    this.selectedPipeline = pipeline;
  }

  runPipeline() {
    this.pipelineRunService
      .triggerRun(
        this.data.projectSlug,
        this.data.modelSlug,
        this.selectedPipeline!.id,
        this.configurationForm.value.includeHistory!,
      )
      .subscribe((pipelineRun: PipelineRun) => {
        this.closeDialog();
        this.router.navigate([
          'project',
          this.data.projectSlug,
          'model',
          this.data.modelSlug,
          'pipeline',
          this.selectedPipeline!.id,
          'run',
          pipelineRun.id,
          'logs',
        ]);
      });
  }

  estimateTime(): string {
    if (this.configurationForm.value.includeHistory) {
      return '1-6 hours';
    }
    return '5-10 minutes';
  }

  closeDialog(): void {
    this.dialogRef.close();
  }

  removePipeline(backup: Pipeline): void {
    this.pipelineService
      .removePipeline(
        this.data.projectSlug,
        this.data.modelSlug,
        backup.id,
        this.force,
      )
      .subscribe(() => {
        this.toastService.showSuccess(
          'Backup pipeline deleted',
          `The pipeline with the ID ${backup.id} has been deleted`,
        );
        this.closeDialog();
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

  viewLogs(backup: Pipeline): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
        job_id: 'backup.lastrun.id',
        backup_id: backup.id,
      } as ViewLogsData,
    });
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
        this.pipelineService
          .loadPipelines(this.data.projectSlug, this.data.modelSlug)
          .subscribe();
      }
    });
  }
}
