import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
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
    public dialog: MatDialog
  ) {}

  @Input()
  project: string = '';

  ngOnInit(): void {}

  backups: Array<Backup> = [
    {
      id: 10,
      t4cmodel: 'Test',
      lastrun: {
        id: 'xy',
        date: 'today',
        state: 'Running',
      },
      gitmodel: 'xy',
    },
    {
      id: 10,
      t4cmodel: 'Test',
      lastrun: {
        id: 'xyz',
        date: 'yesterday',
        state: 'Failed',
      },
      gitmodel: 'xy',
    },
  ];

  createNewBackup(): void {
    this.dialog.open(CreateEASEBackupComponent, {
      data: {},
    });
  }

  runJob(): void {}

  removeBackup(): void {}

  viewLogs(job: BackupJob): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: { jobid: job.id },
    });
  }
}

export interface BackupJob {
  id: string;
  date: string;
  state: string;
}

export interface Backup {
  id: number;
  t4cmodel: string;
  gitmodel: string;
  lastrun: BackupJob;
}
