/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { timer } from 'rxjs';
import { tap } from 'rxjs/operators';
import { BackupService } from 'src/app/projects/models/backup-settings/service/backup.service';

@UntilDestroy()
@Component({
  selector: 'app-view-logs-dialog',
  templateUrl: './view-logs-dialog.component.html',
  styleUrls: ['./view-logs-dialog.component.css'],
})
export class ViewLogsDialogComponent implements OnInit {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: ViewLogsData,
    private easeBackupService: BackupService
  ) {}

  loading = true;
  logs = '';

  ngOnInit(): void {
    timer(0, 5000)
      .pipe(
        tap(() => this.refreshLogs()),
        untilDestroyed(this)
      )
      .subscribe();
  }

  refreshLogs(): void {
    this.loading = true;
    this.easeBackupService
      .getLogs(this.data.projectSlug, this.data.backup_id, this.data.modelSlug)
      .subscribe({
        next: (res: string) => {
          this.loading = false;
          this.logs = res;
        },
        error: () => {
          this.loading = false;
          this.logs = "Couldn't fetch logs";
        },
      });
  }
}

export type ViewLogsData = {
  projectSlug: string;
  modelSlug: string;
  job_id: string;
  backup_id: number;
};
