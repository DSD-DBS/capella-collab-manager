/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface ConfirmationDialogData {
  title: string;
  text: string;
  requiredInput?: string;
}

@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
})
export class ConfirmationDialogComponent implements OnInit {
  inputText: string = '';

  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent, boolean>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmationDialogData
  ) {}

  ngOnInit(): void {
    this.dialogRef.updateSize('500px');
  }

  onSubmit(): void {
    if (this.isSubmitAllowed()) {
      this.dialogRef.close(true);
    }
  }

  onCancelClick(): void {
    this.dialogRef.close(false);
  }

  isSubmitAllowed(): boolean {
    return (
      !this.data.requiredInput || this.inputText === this.data.requiredInput
    );
  }
}
