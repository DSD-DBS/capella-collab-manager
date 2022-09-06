/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Inject } from '@angular/core';

@Component({
  selector: 'app-file-exists-dialog',
  templateUrl: './file-exists-dialog.component.html',
  styleUrls: ['./file-exists-dialog.component.css'],
})
export class FileExistsDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<FileExistsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public filename: string
  ) {}

  ngOnInit(): void {}
}
