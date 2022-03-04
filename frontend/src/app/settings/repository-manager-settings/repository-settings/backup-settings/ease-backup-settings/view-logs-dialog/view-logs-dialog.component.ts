import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-view-logs-dialog',
  templateUrl: './view-logs-dialog.component.html',
  styleUrls: ['./view-logs-dialog.component.css'],
})
export class ViewLogsDialogComponent implements OnInit {
  constructor(@Inject(MAT_DIALOG_DATA) public data: ViewLogsData) {}

  ngOnInit(): void {}
}

export interface ViewLogsData {
  jobid: string;
}
