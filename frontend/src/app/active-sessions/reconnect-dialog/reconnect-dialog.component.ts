import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Session } from 'src/app/schemes';

@Component({
  selector: 'app-reconnect-dialog',
  templateUrl: './reconnect-dialog.component.html',
  styleUrls: ['./reconnect-dialog.component.css'],
})
export class ReconnectDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<ReconnectDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {}

  ngOnInit(): void {}
}
