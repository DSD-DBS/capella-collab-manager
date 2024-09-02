/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormField } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';

export interface ConfirmationDialogData {
  title: string;
  text: string;
  requiredInput?: string;
}

@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
  standalone: true,
  imports: [FormsModule, MatFormField, MatInput, MatButton],
})
export class ConfirmationDialogComponent implements OnInit {
  inputText: string = '';

  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent, boolean>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmationDialogData,
  ) {}

  ngOnInit(): void {
    this.dialogRef.updateSize('500px');
  }

  onSubmit(): void {
    if (this.isSubmitAllowed()) {
      this.dialogRef.close(true);
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  isSubmitAllowed(): boolean {
    return (
      !this.data.requiredInput || this.inputText === this.data.requiredInput
    );
  }
}
