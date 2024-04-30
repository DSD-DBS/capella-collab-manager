/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-file-exists-dialog',
  templateUrl: './file-exists-dialog.component.html',
  styleUrls: ['./file-exists-dialog.component.css'],
  standalone: true,
  imports: [MatButton],
})
export class FileExistsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<FileExistsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public filename: string,
  ) {}
}
