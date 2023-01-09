/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import {
  MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA,
  MatLegacyDialogRef as MatDialogRef,
} from '@angular/material/legacy-dialog';
import { GitSetting } from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-delete-git-settings-dialog',
  templateUrl: './delete-git-settings-dialog.component.html',
  styleUrls: ['./delete-git-settings-dialog.component.css'],
})
export class DeleteGitSettingsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public instance: GitSetting
  ) {}
}
