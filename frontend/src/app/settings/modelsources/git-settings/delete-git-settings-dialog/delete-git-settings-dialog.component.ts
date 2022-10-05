/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GitSetting } from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-delete-git-settings-dialog',
  templateUrl: './delete-git-settings-dialog.component.html',
  styleUrls: ['./delete-git-settings-dialog.component.css'],
})
export class DeleteGitSettingsDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public instance: GitSetting
  ) {}

  ngOnInit(): void {}
}
