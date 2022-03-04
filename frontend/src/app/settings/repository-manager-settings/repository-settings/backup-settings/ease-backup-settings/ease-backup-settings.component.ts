import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  EASEBackup,
  EASEBackupJob,
} from 'src/app/services/backups/ease/easebackup.service';
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

  backups: Array<EASEBackup> = [];

  refreshBackups(): void {}

  createNewBackup(): void {
    const dialogRef = this.dialog.open(CreateEASEBackupComponent, {
      data: {},
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshBackups();
    });
  }

  runJob(): void {}

  removeBackup(): void {}

  viewLogs(job: EASEBackupJob): void {
    this.dialog.open(ViewLogsDialogComponent, {
      data: { jobid: job.id },
    });
  }
}
