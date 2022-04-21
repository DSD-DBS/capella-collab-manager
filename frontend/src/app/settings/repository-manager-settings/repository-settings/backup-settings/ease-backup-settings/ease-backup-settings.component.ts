// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  EASEBackup,
  EASEBackupJob,
  EASEBackupService,
} from 'src/app/services/backups/ease/easebackup.service';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
import { SessionService } from 'src/app/services/session/session.service';
import { CreateEASEBackupComponent } from './create-ease-backup/create-ease-backup.component';
import { ViewLogsDialogComponent } from './view-logs-dialog/view-logs-dialog.component';

@Component({
  selector: 'app-ease-backup-settings',
  templateUrl: './ease-backup-settings.component.html',
  styleUrls: ['./ease-backup-settings.component.css'],
})
export class GitBackupSettingsComponent implements OnInit {
  constructor(
    public beautifyService: BeautifyService,
    public dialog: MatDialog,
    public easeBackupService: EASEBackupService
  ) {}

  @Input()
  project: string = '';

  loading = false;

  ngOnInit(): void {
    this.refreshBackups();
  }

  backups: Array<EASEBackup> = [];

  refreshBackups(): void {
    this.loading = true;
    this.easeBackupService
      .getBackups(this.project)
      .subscribe((res: Array<EASEBackup>) => {
        this.backups = res;
        this.loading = false;
      });
  }

  createNewBackup(): void {
    const dialogRef = this.dialog.open(CreateEASEBackupComponent, {
      data: { project: this.project },
    });

    dialogRef.afterClosed().subscribe((success) => {
      if (success) {
        this.refreshBackups();
      }
    });
  }

  runJob(backup: EASEBackup): void {
    this.easeBackupService.triggerRun(this.project, backup.id).subscribe(() => {
      this.refreshBackups();
    });
  }

  removeBackup(backup: EASEBackup): void {
    this.easeBackupService
      .removeBackup(this.project, backup.id)
      .subscribe(() => {
        this.refreshBackups();
      });
  }

  viewLogs(backup: EASEBackup): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: {
        job_id: backup.lastrun.id,
        backup_id: backup.id,
        project: this.project,
      },
    });
  }
}
