/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface InputDialogData {
  title: string;
  text: string;
}

export interface InputDialogResult {
  text?: string;
  success: boolean;
}

@Component({
  selector: 'app-input-dialog',
  templateUrl: './input-dialog.component.html',
})
export class InputDialogComponent implements OnInit {
  form = new FormGroup({
    result: new FormControl<string | undefined>(undefined, [
      Validators.required,
    ]),
  });

  constructor(
    public dialogRef: MatDialogRef<InputDialogComponent, InputDialogResult>,
    @Inject(MAT_DIALOG_DATA) public data: InputDialogData,
  ) {}

  ngOnInit(): void {
    this.dialogRef.updateSize('500px');
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.dialogRef.close({ text: this.form.value.result!, success: true });
    }
  }

  onCancel(): void {
    this.dialogRef.close({ text: undefined, success: false });
  }
}
