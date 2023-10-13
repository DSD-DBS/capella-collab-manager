/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-file-exists-dialog',
  templateUrl: './file-exists-dialog.component.html',
  styleUrls: ['./file-exists-dialog.component.css'],
})
export class FileExistsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<FileExistsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public filename: string,
  ) {}
}
