/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { GitInstance } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@Component({
  selector: 'app-delete-git-settings-dialog',
  templateUrl: './delete-git-settings-dialog.component.html',
  styleUrls: ['./delete-git-settings-dialog.component.css'],
})
export class DeleteGitSettingsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public instance: GitInstance,
  ) {}
}
