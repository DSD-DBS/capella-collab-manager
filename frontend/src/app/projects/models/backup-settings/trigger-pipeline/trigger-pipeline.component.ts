/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { CreateBackupComponent } from '../create-backup/create-backup.component';
import { BackupService, Pipeline } from '../service/backup.service';
import {
  ViewLogsDialogComponent,
  ViewLogsData,
} from '../view-logs-dialog/view-logs-dialog.component';

@Component({
  selector: 'app-trigger-pipeline',
  templateUrl: './trigger-pipeline.component.html',
  styleUrls: ['./trigger-pipeline.component.css'],
})
export class TriggerPipelineComponent implements OnInit {
  selectedPipeline?: Pipeline = undefined;

  configurationForm = new FormGroup({
    includeHistory: new FormControl(false),
  });

  constructor(
    private toastService: ToastService,
    private dialogRef: MatDialogRef<TriggerPipelineComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string },
    public dialog: MatDialog,
    public backupService: BackupService,
    public sessionService: SessionService
  ) {}

  ngOnInit(): void {
    this.backupService
      .getBackups(this.data.projectSlug, this.data.modelSlug)
      .subscribe();
  }

  selectPipeline(pipeline: Pipeline) {
    this.selectedPipeline = pipeline;
  }

  runPipeline() {
    this.backupService
      .triggerRun(
        this.data.projectSlug,
        this.data.modelSlug,
        this.selectedPipeline!.id,
        this.configurationForm.value.includeHistory!
      )
      .subscribe(() => {
        this.toastService.showSuccess(
          'Pipeline triggered',
          'You can check the current status in the pipeline settings.'
        );
        this.closeDialog();
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

  removeBackup(backup: Pipeline): void {
    this.backupService
      .removeBackup(this.data.projectSlug, this.data.modelSlug, backup.id)
      .subscribe(() => {
        this.toastService.showSuccess(
          'Backup pipeline deleted',
          `The pipeline with the ID ${backup.id} has been deleted`
        );
        this.closeDialog();
      });
  }

  viewLogs(backup: Pipeline): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
        job_id: backup.lastrun.id,
        backup_id: backup.id,
      } as ViewLogsData,
    });
  }

  createNewBackup(): void {
    const dialogRef = this.dialog.open(CreateBackupComponent, {
      data: {
        projectSlug: this.data.projectSlug,
        modelSlug: this.data.modelSlug,
      },
    });

    dialogRef.afterClosed().subscribe((success) => {
      if (success) {
        this.backupService
          .getBackups(this.data.projectSlug, this.data.modelSlug)
          .subscribe();
      }
    });
  }
}
