import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EASEBackupService } from 'src/app/services/backups/ease/easebackup.service';

@Component({
  selector: 'app-view-logs-dialog',
  templateUrl: './view-logs-dialog.component.html',
  styleUrls: ['./view-logs-dialog.component.css'],
})
export class ViewLogsDialogComponent implements OnInit {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: ViewLogsData,
    private easeBackupService: EASEBackupService
  ) {}

  loading = true;
  logs = '';

  ngOnInit(): void {
    this.refreshLogs();
  }

  refreshLogs(): void {
    this.easeBackupService
      .getLogs(this.data.project, this.data.backup_id, this.data.job_id)
      .subscribe(
        (res: string) => {
          this.loading = false;
          this.logs = res;
        },
        () => {
          this.loading = false;
          this.logs = "Couldn't fetch logs";
        }
      );
  }
}

export interface ViewLogsData {
  job_id: string;
  backup_id: number;
  project: string;
}
