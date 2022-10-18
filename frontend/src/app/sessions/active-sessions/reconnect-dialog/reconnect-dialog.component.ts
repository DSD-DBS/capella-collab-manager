/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Session } from 'src/app/schemes';

@Component({
  selector: 'app-reconnect-dialog',
  templateUrl: './reconnect-dialog.component.html',
  styleUrls: ['./reconnect-dialog.component.css'],
})
export class ReconnectDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ReconnectDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {}
}
