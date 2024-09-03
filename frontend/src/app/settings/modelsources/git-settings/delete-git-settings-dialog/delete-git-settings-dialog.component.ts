/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { GitInstance } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@Component({
  selector: 'app-delete-git-settings-dialog',
  templateUrl: './delete-git-settings-dialog.component.html',
  styleUrls: ['./delete-git-settings-dialog.component.css'],
  standalone: true,
  imports: [MatButton],
})
export class DeleteGitSettingsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public instance: GitInstance,
  ) {}
}
