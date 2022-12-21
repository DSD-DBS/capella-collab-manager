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
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { SessionService } from 'src/app/services/session/session.service';
import { CreateBackupComponent } from '../create-backup/create-backup.component';
import { BackupService, Pipeline } from '../service/backup.service';
import { ViewLogsDialogComponent } from '../view-logs-dialog/view-logs-dialog.component';

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
    @Inject(MAT_DIALOG_DATA) public data: { model: Model },
    public dialog: MatDialog,
    public backupService: BackupService,
    public sessionService: SessionService,
    private modelService: ModelService,
    private projectService: ProjectService
  ) {}

  ngOnInit(): void {
    this.modelService._model.next(this.data.model);
    this.backupService
      .getBackups(
        this.projectService.project!.slug,
        this.modelService.model!.slug
      )
      .subscribe();
  }

  selectPipeline(pipeline: Pipeline) {
    this.selectedPipeline = pipeline;
  }

  runPipeline() {
    this.backupService
      .triggerRun(
        this.projectService.project!.slug,
        this.modelService.model!.slug,
        this.selectedPipeline!.id,
        this.configurationForm.value.includeHistory!
      )
      .subscribe(() => {
        this.toastService.showSuccess(
          'Pipeline triggered',
          'You can check the current status in the pipeline settings.'
        );
        this.dialogRef.close();
      });
  }

  estimateTime(): string {
    if (this.configurationForm.value.includeHistory) {
      return '1-6 hours';
    } else {
      return '5-10 minutes';
    }
  }

  closeDialog(): void {
    this.dialogRef.close();
  }

  removeBackup(backup: Pipeline): void {
    this.backupService
      .removeBackup(
        this.projectService.project!.slug,
        this.modelService.model!.slug,
        backup.id
      )
      .subscribe(() => {
        this.toastService.showSuccess(
          'Backup pipeline deleted',
          `The pipeline with the ID ${backup.id} has been deleted`
        );
        this.dialogRef.close();
      });
  }

  viewLogs(backup: Pipeline): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: {
        modelSlug: this.modelService.model!.slug,
        job_id: backup.lastrun.id,
        backup_id: backup.id,
        project: this.projectService.project!.slug,
      },
    });
  }

  createNewBackup(): void {
    const dialogRef = this.dialog.open(CreateBackupComponent, {
      data: { project: this.projectService.project!.slug },
    });

    dialogRef.afterClosed().subscribe((success) => {
      if (success) {
        this.backupService
          .getBackups(
            this.projectService.project!.slug,
            this.modelService.model!.slug
          )
          .subscribe();
      }
    });
  }
}
