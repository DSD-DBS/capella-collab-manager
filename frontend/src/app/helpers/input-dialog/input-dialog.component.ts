/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';

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
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatButton,
  ],
})
export class InputDialogComponent implements OnInit {
  dialogRef =
    inject<MatDialogRef<InputDialogComponent, InputDialogResult>>(MatDialogRef);
  data = inject<InputDialogData>(MAT_DIALOG_DATA);

  form = new FormGroup({
    result: new FormControl<string | undefined>(undefined, [
      Validators.required,
    ]),
  });

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
