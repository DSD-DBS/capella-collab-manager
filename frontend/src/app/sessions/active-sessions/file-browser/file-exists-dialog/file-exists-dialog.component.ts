/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import {
  MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA,
  MatLegacyDialogRef as MatDialogRef,
} from '@angular/material/legacy-dialog';

@Component({
  selector: 'app-file-exists-dialog',
  templateUrl: './file-exists-dialog.component.html',
  styleUrls: ['./file-exists-dialog.component.css'],
})
export class FileExistsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<FileExistsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public filename: string
  ) {}
}
